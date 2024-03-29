from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.http import HttpResponse
from django.http import JsonResponse
from playwright.sync_api import sync_playwright

from .forms import UserRegisterForm, UserUpdateForm, TaskForm, ProductSearchForm
from .models import Task, Product, AliexpressProduct

# Create your views here.
auth = ''
browser_url = f''

@login_required
def home(request):
    all_tasks = Task.objects.order_by('position')
    tasks = all_tasks.filter(owner=request.user)
    task_count = tasks.count()

    status_counts = {}
    for status, _ in Task.STATUS_CHOICES:
        status_counts[status] = tasks.filter(status=status).count()

    not_started = status_counts['NOT_STARTED']
    completed = status_counts['COMPLETED']

    total_tasks = not_started + completed

    if total_tasks > 0:
        percentage_of_tasks = (completed / total_tasks) * 100
        # Cap the percentage at 100%
        percentage_of_tasks = min(percentage_of_tasks, 100)
        formatted_percentage = "{:.2f}".format(percentage_of_tasks)
    else:
        formatted_percentage = "0.00"

    print('not started: ' + str(not_started))
    print('completed: ' + str(completed))
    print('formatted_percentage: ' + formatted_percentage)

    context = {
        'tasks': tasks,
        'task_count': task_count,
        'formatted_percentage': formatted_percentage,
    }

    return render(request, 'home.html', context)

def index(request):
    return render(request, 'index.html')

def tables(request):
    return render(request, 'tables.html')

def newsletter(request):
    return render(request, 'adds/newsletter.html')

def ai_gen(request):
    return render(request, 'adds/ai_gen.html')

def jo_cards(request):
    return render(request, 'adds/jo_cards.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.success(request, "Invalid username or password.")

    return render(request, 'authentication/login.html')

def login_with_email(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'authentication/login_with_email.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def user_register(request):
        if request.method == 'POST':
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                username = form.cleaned_data.get('username')
                if User.objects.filter(email=email) and User.objects.filter(username=username).exists():
                    messages.error(request, 'This email is already registered.')
                    return redirect('user_register')
                else:
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
                    activateEmail(request, user, form.cleaned_data.get('email'))
                    return redirect('sending_activate_token')
        else:
            form = UserRegisterForm()
        context = {
            'form': form,
        }
        return render(request, 'authentication/register.html', context)

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for confirming your email. You can now log in to your account.')
        return redirect('user_login')
    else:
        messages.error(request, 'The activation link is not valid!')
    
    return render(request, 'authentication/login.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('authentication/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = "html"  
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email} and click on the activation link you received to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, please check if you entered it correctly.')

def sending_activate_token(request):
    return render(request, 'authentication/sending_activate_token.html')

def forgot_password(request):
    return render(request, 'forgot_password.html')

async def a_analytics(request):
    async with async_playwright() as pw:
        print('connecting')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print('connected')
        page = await browser.new_page()
        print('goto')
        await page.goto('https://www.amazon.com/Best-Sellers/zgbs/', timeout=120000)
        print('done, evaluating')
        # Extract product names
        context = {
            'product_names': await page.eval_on_selector_all('.a-link-normal .p13n-sc-truncated', 'elements => elements.map(e => e.textContent.trim())'),
        }
        # product_names = await page.eval_on_selector_all('.a-link-normal .p13n-sc-truncated', 'elements => elements.map(e => e.textContent.trim())')
        await browser.close()
    return await sync_to_async(render)(request, 'spiders/a_analytics.html', context)

def scrape_amazon_product(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # browser = p.chromium.launch()

        page = browser.new_page()

        # Navigate to Amazon and search for the product
        page.goto('https://www.amazon.com/')
        page.fill('input[name="field-keywords"]', query)
        page.click('input[type="submit"]')

        # Wait for the results to load
        page.wait_for_selector('span.a-text-normal', timeout=60000)
        # page.wait_for_selector('span.a-text-normal')

        # Extract details for all products
        products_data = page.eval_on_selector_all('.s-result-item', '''elements => {
            return elements.map(element => {
                let title = element.querySelector('span.a-text-normal')?.textContent.trim();
                let price = element.querySelector('span.a-price-whole')?.textContent.trim();
                let imageUrl = element.querySelector('img.s-image')?.getAttribute('src');
                
                // Extract star ratings
                let starRatingElement = element.querySelector('span.a-icon-alt');
                let starRating = starRatingElement ? starRatingElement.textContent.trim() : null;
                
                // Extract number of reviews
                let reviewCountElement = element.querySelector('span[aria-label] > span.a-size-base.s-underline-text');
                let reviewCount = reviewCountElement ? reviewCountElement.textContent.trim().replace('(', '').replace(')', '').replace('K+', '000') : null;
                
                let productUrl = element.querySelector('a.a-link-normal.a-text-normal')?.getAttribute('href');

                return {
                    title: title,
                    price: price ? parseFloat(price.replace(',', '')) : null,
                    image_url: imageUrl,
                    star_rating: starRating,
                    review_count: reviewCount,
                    product_url: productUrl ? `https://www.amazon.com${productUrl}` : null
                };
            });
        }''')

        browser.close()

        return products_data

def scrape_aliexpress_product(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to AliExpress and search for the product
        page.goto('https://www.aliexpress.com/')
        page.fill('input[name="SearchText"]', query)
        page.click('input[type="submit"]')

        # # Check for the age confirmation popup and dismiss it
        # age_popup_selector = 'SELECTOR_FOR_THE_POPUP'  # Replace with the actual selector for the popup
        # yes_button_selector = 'SELECTOR_FOR_YES_BUTTON'  # Replace with the actual selector for the "Yes" button
        
        # if page.is_visible(age_popup_selector, timeout=5000):  # Wait for 5 seconds to check for the popup
        #     page.click(yes_button_selector)

        # Wait for the results to load
        page.wait_for_selector('h1.manhattan--titleText--WccSjUS', timeout=120000)

        # Extract details for all products (you'll need to adjust the selectors based on AliExpress's structure)
        products_data = page.eval_on_selector_all('.list-item', '''elements => {
            return elements.map(element => {
                let titleElement = element.querySelector('h1.manhattan--titleText--WccSjUS');
                let title = titleElement ? titleElement.textContent.trim() : null;

                                                  
                // Extracting price
                let priceSymbolElement = element.querySelector('div.manhattan--price-sale--1CCSZfK span:nth-child(1)');
                let priceMainElement = element.querySelector('div.manhattan--price-sale--1CCSZfK span:nth-child(2)');
                let priceDecimalElement = element.querySelector('div.manhattan--price-sale--1CCSZfK span:nth-child(4)');
                
                let priceSymbol = priceSymbolElement ? priceSymbolElement.textContent.trim() : '';
                let priceMain = priceMainElement ? priceMainElement.textContent.trim() : '';
                let priceDecimal = priceDecimalElement ? priceDecimalElement.textContent.trim() : '';
                
                let price = priceSymbol + priceMain + (priceDecimal ? ',' + priceDecimal : '');

                return {
                    title: title,
                    price: price,

                };
            });
        }''')


        browser.close()

        return products_data

# @login_required
# def search_product(request):
#     if request.method == 'POST':
#         form = ProductSearchForm(request.POST)
#         if form.is_valid():
#             products_data = scrape_amazon_product(form.cleaned_data['query'])
#             # Filter out products without a price
#             products_data = [data for data in products_data if data['price'] is not None]
#             products = [Product.objects.create(**data) for data in products_data]
#             return render(request, 'spiders/product_detail.html', {'products': products})
#     else:
#         form = ProductSearchForm()
#     return render(request, 'spiders/search_product.html', {'form': form})

@login_required
def search_product(request):
    if request.method == 'POST':
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            amazon_products = scrape_amazon_product(form.cleaned_data['query'])
            aliexpress_products = scrape_aliexpress_product(form.cleaned_data['query'])

            # Print the scraped AliExpress products
            print("AliExpress Products:", aliexpress_products)

            # Filter out products without a price (for both Amazon and AliExpress)
            amazon_products = [data for data in amazon_products if data['price'] is not None]
            aliexpress_products = [data for data in aliexpress_products if data['price'] is not None]

            amazon_db_products = [Product.objects.create(**data) for data in amazon_products]
            aliexpress_db_products = [AliexpressProduct.objects.create(**data) for data in aliexpress_products]

            return render(request, 'spiders/product_detail.html', {
                'amazon_products': amazon_db_products,
                'aliexpress_products': aliexpress_db_products
            })
    else:
        form = ProductSearchForm()
    return render(request, 'spiders/search_product.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'autho/profile.html')

@login_required
def tasks(request):
    all_tasks = Task.objects.order_by('position')
    tasks = all_tasks.filter(owner=request.user)
    task_count = tasks.count()

    status_counts = {}
    for status, _ in Task.STATUS_CHOICES:
        status_counts[status] = tasks.filter(status=status).count()

    context = {
        'tasks': tasks,
        'task_count': task_count,
        'status_counts': status_counts,
    }
    return render(request, 'service/tasks.html', context)

def update_task_order(request):
    """
    Handle the request to update the order and status of tasks.

    This view expects a POST request with 'item' and 'status' data.
    'item' contains the IDs of tasks in their current order.
    'status' contains the status of each task.

    The function updates the position and status of each task in the database.
    """
    # Check if the request method is POST.
    if request.method == "POST":
        
        # Extract the list of task IDs from the POST data.
        items = request.POST.getlist('item')
        
        # Extract the list of statuses from the POST data.
        statuses = request.POST.getlist('status')
        
        # Print the received items and statuses for debugging purposes.
        print("Received items:", items)  
        print("Received statuses:", statuses) 
        
        # Loop through each task ID and status.
        for index, (item_id, status) in enumerate(zip(items, statuses)):
            
            # Fetch the task object from the database using its ID.
            task = Task.objects.get(id=item_id)
            
            # Update the task's position based on its order in the received list.
            task.position = index
            
            # Update the task's status.
            task.status = status
            
            # Save the updated task to the database.
            task.save()

    # Return a 204 No Content response to indicate successful processing.
    return HttpResponse(status=204)

def items_detail(request, pk):
    task = get_object_or_404(Task, id=pk)
    context = {
        'task': task,
    }
    return render(request, 'service/items_detail.html', context)

@login_required
def create_task(request):
    if request.method == 'POST':
        form_task = TaskForm(request.POST)
        if form_task.is_valid():
            task = form_task.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('tasks')
    else: 
        form_task = TaskForm(request.POST)
    
    context = {
        'form_task': form_task,
    }
    return render(request, 'service/create_task.html', context)

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk, owner=request.user)  # Ensure the task belongs to the logged-in user
    if request.method == 'POST':  # Confirm the task deletion with a POST request
        task.delete()
        return redirect('tasks')  # Redirect to the tasks view after deletion
    context = {
        'task': task,
    }
    return render(request, 'service/confirm_delete.html', context)

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, id=pk, owner=request.user)  # Ensure the task belongs to the logged-in user
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')  
    else:
        form = TaskForm(instance=task) 
    context = {
        'form': form,
        'task': task,
    }
    return render(request, 'service/edit_task.html', context)

def settings(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('settings')  # Redirect to the same profile page or any other page you want
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form,
    }
    return render(request, 'autho/settings.html', context)

def terms_of_service(request):
    return render(request, 'autho/terms_of_service.html')

def email_service(request):
    return render(request, 'autho/email_service.html')

def test_decor_page(request):
    return render(request, 'test_decor_page.html')
