from .utilities import login_requirements
from django.http import JsonResponse
from .forms import CreatePostForm
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse
from apps.app_notification.models import Notification, NoticeCategory

from apps.app_users.models import Profile, User
from .models import Posts, Like, Comment, FriendRequests, Friends, PostImage, SavedPost
from .forms import FriendRequestsForm,FriendsForm, PostImageForm

from django.db.models import Q, Case, When, IntegerField, F, Count
from django.utils import timezone
from datetime import timedelta
from .moderation import is_toxic_text
from .transcribe import transcribe_video
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# UPDATED: 8/06/2025
@login_requirements()
def homepage(request):
    # Current logged in user profile
    profile = request.user.profile

    #  user's friends
    existing_friend_object = Friends.objects.filter(author=profile).first()
    friend_profiles = existing_friend_object.friend.all() if existing_friend_object else []
    friend_ids = [friend.uid for friend in friend_profiles]
    
    #  intelligent newsfeed
    all_post = Posts.objects.select_related('author').prefetch_related(
        'images', 'likes', 'comments'
    ).annotate(
        # Count likes and comments for engagement score
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
        
        # Priority scoring system
        priority_score=Case(
            # Own posts get highest priority
            When(author=profile, then=100),
            # Friends' posts get high priority
            When(author__uid__in=friend_ids, then=50),
            # Other posts get base priority
            default=10,
            output_field=IntegerField()
        ),
        
        # Time-based scoring (newer posts get higher scores)
        time_score=Case(
            When(created_at__gte=timezone.now() - timedelta(hours=24), then=20),
            When(created_at__gte=timezone.now() - timedelta(days=7), then=10),
            When(created_at__gte=timezone.now() - timedelta(days=30), then=5),
            default=1,
            output_field=IntegerField()
        )
    ).annotate(
        # Final score calculation
        final_score=F('priority_score') + F('time_score') + F('likes_count') + F('comments_count')
    ).order_by('-final_score', '-created_at')

    # Friend suggestions (exclude current friends and pending requests)
    people = Profile.objects.filter(
        fill_up=True, 
        registered=True
    ).exclude(
        Q(uid=profile.uid) |  # Exclude self
        Q(uid__in=friend_ids)  # Exclude existing friends
    )

    # Filtering the friend request sent list
    my_requests = FriendRequests.objects.filter(sender=profile)
    request_lists = [x.author for x in my_requests]
    
    friends = existing_friend_object.friend.all() if existing_friend_object else None
    got_requests = FriendRequests.objects.filter(author=profile)

    # Handle POST request for creating posts
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            the_form = form.save(commit=False)
            the_form.author = profile
            if is_toxic_text(the_form.content):
                messages.error(request, "Your post seems to contain toxic language and was not posted.")
                return redirect(request.path)
            the_form.save()

            image_no = request.POST.get('last_image')
            if image_no:
                try:
                    for x in range(int(image_no)):
                        the_image = request.FILES.get(f'image_{x+1}')
                        if the_image:                      
                            post_image_object = PostImage.objects.create(post=the_form)
                            post_image_object.image = the_image
                            post_image_object.save()
                            # optional transcription for videos
                            if post_image_object.is_video:
                                txt = transcribe_video(post_image_object.image.path)
                                if txt:
                                    post_image_object.transcript = txt
                                    post_image_object.save(update_fields=["transcript"])
                    messages.success(request, "Post with Images uploaded successfully!")
                except Exception as e:
                    messages.warning(request, f"Something went wrong, So Images did not uploaded, But post uploaded.")

            messages.success(request, "Post uploaded!")
            return redirect(request.path)
        else:
            # Allow media-only posts (no text)
            image_no = request.POST.get('last_image')
            if image_no:
                the_form = Posts.objects.create(author=profile, content=request.POST.get('content',''), privacy=request.POST.get('privacy','public'))
                try:
                    for x in range(int(image_no)):
                        the_image = request.FILES.get(f'image_{x+1}')
                        if the_image:
                            pi = PostImage.objects.create(post=the_form, image=the_image)
                            if pi.is_video:
                                txt = transcribe_video(pi.image.path)
                                if txt:
                                    pi.transcript = txt
                                    pi.save(update_fields=["transcript"])
                    messages.success(request, "Post uploaded!")
                except Exception as e:
                    messages.warning(request, f"Media upload failed: {e}")
                return redirect(request.path)
    else:
        form = CreatePostForm()

    context = {
        "posts": all_post,
        "people": people,
        "request_list": request_lists,
        "got_requests": got_requests,
        "friends": friends,
        "form": form,
    }
    return render(request, "home/main/index.html", context)


# ii) When accepting or rejecting request we can send notifications
@login_requirements()
def accept_request(request, usr):
    '''
    usr -> is he/ she who sender request or him/her username.
    By getting both sender and receiver profile friend list is getting updated.
    '''
    myself = request.user.profile
    try:
        themself = get_object_or_404(Profile, user__username=usr.strip())
        # ---- LOGGED IN USER'S (My) FRIEND ADDING ----->>
        my_existing_object = Friends.objects.get_or_create(author=myself)[0]    
        my_existing_object.friend.add(themself)

        # # ---- ALSO ADDING FRIEND FOR THAT PERSON WHO REQUESTED ---->>>
        them_existing_object = Friends.objects.get_or_create(author=themself)[0]
        them_existing_object.friend.add(myself)
        messages.success(request, f"{themself} added as friend!")

        # Notify the sender that their friend request was accepted
        try:
            category, _ = NoticeCategory.objects.get_or_create(name="friend_request")
            Notification.objects.create(
                notice_for=themself,  # notify the original sender
                notification=f"{myself.first_name} accepted your friend request",
                link=request.build_absolute_uri(reverse('view_profile', args=[request.user.username])),
                category=category,
            )
        except Exception:
            pass
    except Exception as e:
        messages.error(request, f" {e} !")
        print("accept req function's first try catch ===>>> ", e)
        
    try:
        FriendRequests.objects.filter(author=myself, sender=themself)[0].delete()
        FriendRequests.objects.filter(sender=themself, author=myself)[0].delete()
    except Exception as e:
        print("accept req function's 2nd try catch ===>>> ", e)

    if request.htmx or request.method == "POST":
        # remove the row
        return HttpResponse("")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# i) In case of sending friend request we can check
#    Is the profile is fill_up and registered ?
# ii) When sending request we can send notification
@login_requirements()
def send_friend_request(request):
    if request.method == "POST":
        # print("===>>> ",request.POST.get("the_person"))
        try:
            person = request.POST.get("the_person")
            author_whom_sending_request = get_object_or_404(Profile, user__username=person.strip())
            
            # Check if the friend request already exists
            existing_request = FriendRequests.objects.filter(
                author=author_whom_sending_request,
                sender=request.user.profile
            ).exists()
            
            if not existing_request:
                FriendRequests.objects.create(
                    author=author_whom_sending_request,
                    sender=request.user.profile,
                    requested=True
                )
                messages.success(request, "SUCCESS SEND REQUEST!")
                # Create a notification for the recipient
                try:
                    category, _ = NoticeCategory.objects.get_or_create(name="friend_request")
                    Notification.objects.create(
                        notice_for=author_whom_sending_request,
                        notification=f"{request.user.profile.first_name} sent you a friend request",
                        link=request.build_absolute_uri(reverse('view_profile', args=[request.user.username])),
                        category=category,
                    )
                except Exception:
                    pass
                
            else:
                messages.error(request, "Already in friend request list!")
                
            
            # Redirect back to the referring page
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            messages.warning(request, f"{e}")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_requirements()
def cancel_friend_request(request):
    if request.method == "POST":
        try:
            person = request.POST.get("the_person")
            author_whom_sending_request = get_object_or_404(Profile, user__username=person.strip())
            
            # if the friend request exists
            existing_request = FriendRequests.objects.filter(
                author=author_whom_sending_request,
                sender=request.user.profile
            ).first()
            
            if existing_request:
                existing_request.delete()
                messages.success(request, "Friend request cancelled!")
            else:
                messages.error(request, "No such friend request found!")
                
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            messages.warning(request, f"{e}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@login_requirements()
def view_one_post(request, p_id):
    context={}
    try:
        data = get_object_or_404(Posts, uid=p_id.strip())
        context["data"]=data

    except Exception as e:
        messages.error(request, f" {e}!")

    return render(request, "home/main/view_single_post.html", context)

@login_requirements()
def view_replies(request, cmnt_uid):
    if request.htmx:
        comment = get_object_or_404(Comment,uid=cmnt_uid.strip())
        
        context={
            "comment":comment
        }
        return render(request, "home/partials/reply.html", context)
    
    return HttpResponse("Noting to show with this url",status=400)

@login_requirements()
def create_comments(request, post_uid):
    if request.htmx:
        if request.method == "POST":
            post = get_object_or_404(Posts, uid=post_uid.strip())
            
            try:
                comment_content = request.POST.get('content')                
                
                if comment_content:
                    if is_toxic_text(comment_content):
                        messages.error(request, "Your comment contains toxic language and was not posted.")
                    else:
                        profile = request.user.profile
                        Comment.objects.create(
                            user=profile,
                            post=post,
                            content=comment_content
                        )
                        messages.success(request,"You added a comment")
            except Exception as e:
                messages.warning(request, f" {e}!")
        
        context = {
            "data": post
        }
        return render(request, "home/partials/comments.html", context)
    
    return HttpResponse("Nothing to show with this url", status=400)

@login_requirements()
def create_reply(request, cmnt_uid):
    parent_comment = Comment.objects.get(uid=cmnt_uid.strip())
    if request.htmx:
        context = {
            "parent":parent_comment
        }
        return render(request, "home/partials/reply_form.html", context)
    
    return HttpResponse("Nothing to show with this url", status=400)

@login_requirements()
def add_reply(request):
    if request.htmx:
        if request.method=="POST":
            try:
                the_reply=request.POST.get('the_reply')
                main_post_uid=request.POST.get('main_post')            
                parent_comment_uid=request.POST.get('parent_comment')            
                parent_comment = get_object_or_404(Comment, uid=parent_comment_uid.strip())
                the_post=get_object_or_404(Posts, uid=main_post_uid.strip())
                Comment.objects.create(
                    post=the_post,
                    user=request.user.profile,
                    content=the_reply,
                    parent=parent_comment,
                )
            except Exception as e:
                messages.error(request, f" {e}!")

        context={
            "data":the_post
        }
        return render(request, "home/partials/comments.html", context)
    
    return HttpResponse("Nothing to show with this url", status=400)

@login_requirements()
def make_a_post(request):
    if request.htmx:
        if request.method=="POST":
            form=CreatePostForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    the_form = form.save(commit=False)
                    the_form.author = request.user.profile
                    if is_toxic_text(the_form.content):
                        messages.error(request, "Your post seems to contain toxic language and was not posted.")
                        return redirect("homepage")
                    the_form.save()
                    return redirect("homepage")
                except Exception as e:
                    messages.error(request, f" {e} !")
        else:
            form=CreatePostForm()
            context={"form":form, "i":0}
            
            return render(request, "home/partials/post_form.html", context)
    else:
        return HttpResponse("Nothing to show with this url", status=400)

# ----------------------------------- POST LIKE RELATED ------------------------------------
@login_requirements()
def like_post(request, post_id):
    post = get_object_or_404(Posts, uid=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user.profile)
    if not created:
        like.delete()
    if request.htmx:
        context={
            "data": post,

        }
        return render(request, "home/partials/liked.html", context)
    else:
        return HttpResponse("Go Back some server misleading!")
    
#UPDATED: 08/06/2025==> API to return those who liked the post
@login_requirements()
def post_likers(request, post_id):
    post = get_object_or_404(Posts, uid=post_id)
    likers = post.likes.select_related('user', 'user__user').all()
    
    # current user's friends for the template
    existing_friend_object = Friends.objects.filter(author=request.user.profile).first()
    friends = existing_friend_object.friend.all() if existing_friend_object else []
    
    # sent friend requests
    my_requests = FriendRequests.objects.filter(sender=request.user.profile)
    request_list = [x.author for x in my_requests]
    
    if request.htmx:
        context = {
            "likers": likers,
            "post": post,
            "friends": friends,
            "request_list": request_list,
        }
        return render(request, "home/partials/post_likers.html", context)
    else:
        return JsonResponse({
            "likers": [
                {
                    "username": liker.user.user.username,
                    "name": f"{liker.user.first_name} {liker.user.last_name}",
                    "profile_picture": liker.user.profile_picture.url if liker.user.profile_picture else None
                } 
                for liker in likers
            ]
        })

# ----------------------------------- POST LIKE RELATED END ------------------------------------

# ---- WORKING - FROM - 18/07/2024 ----- (DONE)
# NOTE: The search functionality can be improved after develop Pages and Groups feature.
# CAN IMPROVE: 2
# ERROR/Bug: 0
@login_requirements()
def search(request):
    '''
    SEARCH FUNCTION - No parameter needed.
    This funtion takes the search argument via GET method from the webpage
    and match the charecter with username contains in the matched query or not.
    '''
    profile = request.user.profile
    qury = request.GET.get('q')
    results = []
    frnd_reqs = FriendRequests.objects.filter(sender=profile, accepted=False)
    got_reqs = FriendRequests.objects.filter(author=profile, accepted=False)
    
    if qury:
       
        results = Profile.objects.filter(Q(user__username__icontains=qury) 
                                         | Q(first_name__icontains=qury) 
                                         | Q(last_name__icontains=qury)
                                         
                                         )
        results=results.filter(registered=True).order_by("first_name")[0:100]
    context={
        "search_results":results,
        "s_query":qury,
        "frnd_reqs":[ x.author for x in frnd_reqs],
        "got_reqs": [ x.sender for x in got_reqs],
    }

    return render(request, "home/main/search.html", context)


# ---- WORKING - FROM - 19/07/2024 ----- (DONE)
# NOTE: Nothing
# CAN IMPROVE: 2  | i) like to the comment ii) load more comment
# ERROR/Bug: 1    | i) reply need to show 

@login_requirements()
def feed_comment(request, post_uid):
    if request.htmx:
        post = get_object_or_404(Posts, uid=post_uid.strip())
        if request.method == "POST":
            try:
                comment_content = request.POST.get('content')                
                
                if comment_content:
                    if is_toxic_text(comment_content):
                        messages.error(request, "Your comment contains toxic language and was not posted.")
                    else:
                        profile = request.user.profile
                        Comment.objects.create(
                            user=profile,
                            post=post,
                            content=comment_content
                        )
                    
            except Exception as e:
                print(f"ERROR - FEED COMMENT: {e}")
                messages.warning(request, f" {e}!")
        try:
            my_comment = Comment.objects.filter(
                user=profile,
                post=post,
                ).order_by("-created_at").first()
            
        except:
            my_comment=None
        context = {
            "data": post,
            "my_comment":my_comment,
        }
        # return redirect("homepage")
        return render(request, "home/partials/feed_comment.html", context)
    return HttpResponse("Don't lost in the --- MORICHIKA ---", status=400)


# ---- WORKING - FROM - 19/07/2024 - 21/07/20204 -----(DONE)
# NOTE: Nothing
# CAN IMPROVE: 2 [i) Only the public privacy posts and images will show insted of all()
#                ii)  
#                ]
# ERROR/Bug: 1 [i) When upload post with Image the image not saving in object]

@login_requirements()
def view_profile(request, name):
    '''
    The function for view user profile and detail. User can make post
    and see friends and edit profile as well. And public view will also 
    show from here.
    '''
    username = name.strip()
    its_user_himself = False
    
    profile = get_object_or_404(Profile, user__username = username)
    he=profile
    me=request.user

    all_post = Posts.objects.filter(author=profile)
    all_photo = PostImage.objects.filter(post__author = profile).order_by("-created_at")[:10]
    if username == me.username:
        its_user_himself = True
    

    form=CreatePostForm()
    
    # From here its logic to make a post with image upload->
    # ISSUE FIXED SUCCESS and Now we will let user upload upto 1 image.
    if request.method=="POST":     
        form=CreatePostForm(request.POST)
        last_img_no = request.POST.get('last_image')
        if form.is_valid():
        
            the_form = form.save(commit=False)
            the_form.author = me.profile
            form.save()
            messages.success(request, "Post content saved!")
            
            if last_img_no:
                try:
                    for x in range(int(last_img_no)):
                        the_image = request.FILES.get(f'image_{x+1}')
                        
                        if the_image:                      
                            post_image_object = PostImage.objects.create(
                                post=the_form,

                            )
                            post_image_object.image = the_image
                            post_image_object.save()
                        
                        # This brake will prevent user to upload more than 1 image,
                        # In production remove break when a dedicated storage will there.
                        break
                    messages.success(request,"Images uploaded successfully!")

                except Exception as e:
                    messages.warning(request, f"Something went wrong, So Images did not uploaded = {e}")
        else:
            if last_img_no:
                # allow media-only posts
                the_form = Posts.objects.create(author=me.profile, content=request.POST.get('content',''), privacy=request.POST.get('privacy','public'))
                try:
                    for x in range(int(last_img_no)):
                        the_image = request.FILES.get(f'image_{x+1}')
                        if the_image:                      
                            post_image_object = PostImage.objects.create(post=the_form)
                            post_image_object.image = the_image
                            post_image_object.save()
                            if post_image_object.is_video:
                                txt = transcribe_video(post_image_object.image.path)
                                if txt:
                                    post_image_object.transcript = txt
                                    post_image_object.save(update_fields=["transcript"])
                    messages.success(request,"Images uploaded successfully!")
                except Exception as e:
                    messages.warning(request, f"Something went wrong, So Images did not uploaded = {e}")
        return redirect(request.path)
    # =====================================
    his_friend_req_list=FriendRequests.objects.filter(
        sender= me.profile,
        author=he,
        accepted=False,
    )
    my_friend_req_list=FriendRequests.objects.filter(
        author=me.profile,
        sender= he,
        accepted=False,
    )
    myfriends = Friends.objects.get_or_create(author=me.profile)[0]
    context={
        "the_profile":profile,
        "its_user_himself":its_user_himself,
        "posts":all_post,
        "all_photo":all_photo,
        "i":0,
        "form":form,
        "his_friend_req_list":[ x.sender for x in his_friend_req_list],
        "my_friend_req_list":[ x.sender for x in my_friend_req_list],
        "myfriends":myfriends,
    }

    return render(request, "home/main/view_profile.html", context)

# 22/07/2024 -- (DONE)
@login_requirements()
def add_post_images(request, itr):
    '''
    HTMX response for show the image upload option to the user.
    Multiple click shows up option of more image add.
    Just for show partials code of image upload option.
    '''
    if request.htmx:
        i = int(itr)+1
        context={"i":i, "accept_type": "image/*", "kind": "image"}
        return render(request, "home/partials/add_media.html",context)
    return HttpResponse("You are lost in BLACK HOLE!", status=404)


@login_requirements()
def add_post_media(request, itr, kind):
    if request.htmx:
        i = int(itr) + 1
        accept = "video/*" if kind == "video" else "image/*"
        context = {"i": i, "accept_type": accept, "kind": kind}
        return render(request, "home/partials/add_media.html", context)
    return HttpResponse("You are lost in BLACK HOLE!", status=404)


# ---- WORKING - FROM - 21/07/2024 -----(DONE)
# NOTE: Nothing
# CAN IMPROVE: 3 [i) after delete redirect where it was 
#                ii) Only the post owner will see the delete option in HTML
#               iii) 
# ]
# ERROR/Bug: 0
@login_requirements()
def delete_post(r, p_id):
    '''
    This function taked post uid and check if the user is actually the
    Post's owner or not, then it delete the post.
    '''
    post = get_object_or_404(Posts, uid=p_id.strip())
    if post.author == r.user.profile:
        try:
            post.delete()
            messages.warning(r, "Your post has been deleted permanently!")
        except:
            messages.error(r, "Something fishy happened! Post could not be deleted!")
    else:
        messages.warning(r, "Whatever you do! You can't delete someone's post!")

    # return redirect("homepage")
    return redirect(r.META.get('HTTP_REFERER', '/'))
    # return JsonResponse({'success': True})


@login_requirements()
def save_post(request, post_id):
    post = get_object_or_404(Posts, uid=post_id)
    saved, created = SavedPost.objects.get_or_create(user=request.user.profile, post=post)
    if not created:
        saved.delete()
        saved_state = False
    else:
        saved_state = True

    if request.htmx:
        # Return a tiny HTML snippet to toggle menu text
        return render(request, "home/partials/save_menu_item.html", {"post": post, "is_saved": saved_state})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_requirements()
def hide_post(request, post_id):
    # For now, just return empty so HTMX can remove the card from DOM
    if request.htmx:
        return HttpResponse("")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_requirements()
def unfollow_user(request, username):
    me = request.user.profile
    target = get_object_or_404(Profile, user__username=username.strip())
    my_friends = Friends.objects.get_or_create(author=me)[0]
    if target in my_friends.friend.all():
        my_friends.friend.remove(target)
    if request.htmx:
        return HttpResponse("")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# =============== TEMPRORARY TESTING ROUTE ====================

def summarize_demo(request):
    from .transcribe import summarize_text
    sample = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "unlike the natural intelligence displayed by humans and animals. Leading AI "
        "textbooks define the field as the study of 'intelligent agents': any device "
        "that perceives its environment and takes actions that maximize its chance of "
        "successfully achieving its goals."
    )
    result = summarize_text(sample) or "No summary generated."
    return HttpResponse(f"<h3>Original:</h3><p>{sample}</p><h3>Summary:</h3><p>{result}</p>")

def sentiment_demo(request):
    from .transcribe import sentiment_analysis
    sample = (
        "Artificial intelligence (AI) is intelligence demonstrated by machines, "
        "unlike the natural intelligence displayed by humans and animals. Leading AI "
        "textbooks define the field as the study of 'intelligent agents': any device "
        "that perceives its environment and takes actions that maximize its chance of "
        "successfully achieving its goals."
    )
    result = sentiment_analysis(sample)
    if result:
        out = f"<b>Polarity:</b> {result['polarity']}<br><b>Subjectivity:</b> {result['subjectivity']}"
    else:
        out = "No sentiment could be calculated. (Did you install textblob?)"
    return HttpResponse(f"<h3>Original:</h3><p>{sample}</p><h3>Sentiment:</h3><p>{out}</p>")

@csrf_exempt
@require_POST
def analyze_sentiment_ajax(request):
    from .transcribe import sentiment_analysis
    content = request.POST.get('content') or ''
    result = sentiment_analysis(content or '')
    if result is None:
        return JsonResponse({'error': 'Analyzer unavailable'}, status=502)
    polarity = result['polarity']
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return JsonResponse({'sentiment': sentiment, 'polarity': polarity, 'subjectivity': result['subjectivity']})