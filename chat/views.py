from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import User
import mimetypes
from .models import Conversation, Message
from posts.models import Post


def _get_other_user(convo, me):
    return convo.user2 if convo.user1 == me else convo.user1


@login_required
def inbox(request):
    user = request.user
    convos = Conversation.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).order_by("-updated")

    rows = []
    for c in convos:
        other = _get_other_user(c, user)
        last_msg = c.messages.order_by("-created").first()
        unread = c.messages.filter(is_read=False).exclude(sender=user).count()
        rows.append({
            "convo": c,
            "other": other,
            "last_msg": last_msg,
            "unread": unread
        })

    return render(request, "chat/inbox.html", {"rows": rows})


@login_required
def chat_room(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    user = request.user

    if not (convo.user1 == user or convo.user2 == user):
        return redirect("chat:chat_inbox")

    other_user = _get_other_user(convo, user)

    # mark incoming read
    convo.messages.filter(is_read=False).exclude(sender=user).update(
        is_read=True, read_at=timezone.now()
    )

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        file = request.FILES.get("attachment")
        if text or file:
            Message.objects.create(
                conversation=convo,
                sender=user,
                text=text,
                attachment=file
            )
            convo.updated = timezone.now()
            convo.save(update_fields=["updated"])
        return redirect("chat:chat_room", convo_id=convo.id)

    messages = convo.messages.select_related(
        "sender", "shared_post", "shared_post__author"
    ).order_by("created")

    return render(request, "chat/room.html", {
        "convo": convo,
        "other_user": other_user,
        "messages": messages,
    })

@login_required
def delete_message(request, msg_id):
    """
    Delete only if sender is current user.
    """
    msg = get_object_or_404(Message, id=msg_id)

    if msg.sender != request.user:
        return HttpResponseForbidden("Not allowed")

    convo_id = msg.conversation.id
    msg.delete()

    # if AJAX delete -> return json
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})

    return redirect("chat:chat_room", convo_id=convo_id)


@login_required
def api_messages(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    user = request.user

    if not (convo.user1 == user or convo.user2 == user):
        return JsonResponse({"error": "not allowed"}, status=403)

    # ✅ realtime seen: viewer ke incoming messages mark read
    convo.messages.filter(is_read=False).exclude(sender=user).update(
        is_read=True,
        read_at=timezone.now()
    )

    msgs = convo.messages.select_related(
        "sender",
        "shared_post",
        "shared_post__author"
    ).order_by("created")

    out = []
    for m in msgs:
        shared = None
        attachment = ""
        atype = ""

        # attachment handling
        if getattr(m, "attachment", None):
            if m.attachment:
                attachment = m.attachment.url
                low = attachment.lower()
                if low.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    atype = "image"
                elif low.endswith((".mp4", ".webm", ".ogg")):
                    atype = "video"
                else:
                    atype = "file"
        
        if m.attachment:
            attachment = m.attachment.url
            mime, _ = mimetypes.guess_type(m.attachment.name)
            if mime and mime.startswith("image/"):
                atype = "image"
            elif mime and mime.startswith("video/"):
                atype = "video"
            else:
                atype = "file"

        # shared post handling
        if m.shared_post:
            sp = m.shared_post
            shared = {
                "id": sp.id,
                "author": sp.author.username,
                "content": sp.content or "",
                "image": sp.image.url if getattr(sp, "image", None) else "",
            }

        out.append({
            "id": m.id,
            "sender": m.sender.username,
            "text": m.text or "",
            "created": m.created.strftime("%b %d, %H:%M"),
            "is_read": m.is_read,

            "shared_post": shared,

            "attachment": attachment,
            "attachment_type": atype,
        })

    return JsonResponse({"messages": out})


@login_required
def api_set_typing(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    user = request.user

    if not (convo.user1 == user or convo.user2 == user):
        return JsonResponse({"error": "not allowed"}, status=403)

    # 5 sec typing
    cache.set(f"typing:{convo_id}:{user.id}", True, timeout=5)
    return JsonResponse({"ok": True})


@login_required
def api_typing(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    user = request.user

    if not (convo.user1 == user or convo.user2 == user):
        return JsonResponse({"error": "not allowed"}, status=403)

    other = _get_other_user(convo, user)
    is_typing = cache.get(f"typing:{convo_id}:{other.id}") is True
    return JsonResponse({"typing": is_typing})


@login_required
def share_post_to_user(request, post_id, username):
    post = get_object_or_404(Post, id=post_id)
    target = get_object_or_404(User, username=username)

    # get/create convo
    convo = Conversation.objects.filter(
        user1__in=[request.user, target],
        user2__in=[request.user, target]
    ).first()

    if not convo:
        convo = Conversation.objects.create(user1=request.user, user2=target)

    # create shared message
    Message.objects.create(
        conversation=convo,
        sender=request.user,
        text="",
        shared_post=post
    )

    # increment share count
    if hasattr(post, "share_count"):
        post.share_count += 1
        post.save(update_fields=["share_count"])

    # go to room
    return redirect("chat:chat_room", convo_id=convo.id)
