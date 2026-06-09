import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from .models import ChatSession, ChatMessage, UploadedDocument
from .serializers import RegisterSerializer, UserSerializer
from .ingestion import ingest_pdf
from .embeddings import store_embeddings
from .rag_chain import ask_question_with_history


# ─── AUTH VIEWS ───────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            })
        return Response({"error": "Invalid username or password"}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user": UserSerializer(request.user).data,
            "total_documents": UploadedDocument.objects.filter(user=request.user).count(),
            "total_sessions": ChatSession.objects.filter(user=request.user).count(),
        })


# ─── DOCUMENT VIEWS ───────────────────────────────────

class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=400)
        if not file.name.endswith('.pdf'):
            return Response({"error": "Only PDF files allowed"}, status=400)

        save_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(save_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        chunks = ingest_pdf(save_path)
        store_embeddings(chunks)

        # Save document record for this user
        UploadedDocument.objects.create(
            user=request.user,
            filename=file.name,
            file_path=save_path
        )

        return Response({
            "message": "PDF uploaded successfully",
            "chunks": len(chunks),
            "filename": file.name
        })


# ─── CHAT VIEWS ───────────────────────────────────────

class NewSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = str(uuid.uuid4())
        ChatSession.objects.create(
            session_id=session_id,
            user=request.user
        )
        return Response({
            "session_id": session_id,
            "message": "New session created"
        })


class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question", "").strip()
        session_id = request.data.get("session_id", "")

        if not question:
            return Response({"error": "No question provided"}, status=400)
        if not session_id:
            return Response({"error": "No session_id provided"}, status=400)

        # Verify session belongs to this user
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        # Get chat history
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        chat_history = [{"role": m.role, "content": m.content} for m in messages]

        # Get answer
        answer = ask_question_with_history(question, chat_history)

        # Save to DB
        ChatMessage.objects.create(session=session, role="user", content=question)
        ChatMessage.objects.create(session=session, role="assistant", content=answer)

        return Response({
            "answer": answer,
            "question": question,
            "session_id": session_id
        })


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(
                session_id=session_id,
                user=request.user
            )
            messages = ChatMessage.objects.filter(session=session).order_by('created_at')
            history = [{"role": m.role, "content": m.content, "time": m.created_at} for m in messages]
            return Response({"session_id": session_id, "history": history})
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "message": "API is running"})