# Vcart — Modern E-Commerce Platform

A high-performance, full-featured e-commerce platform built with **Django 5** and modern **Vanilla CSS**. Vcart combines a customer-facing storefront with a dual-administration system: Django's built-in `/admin/` and a dedicated, staff-only **Store Operations Dashboard** (`/dashboard/`).

---

## 🌐 Live Demo & URLs

| Service / Interface | URL Path | Access Permission |
| :--- | :--- | :--- |
| **Storefront** | [https://vcart-task.onrender.com/](https://vcart-task.onrender.com/) | Public |
| **Operations Dashboard** | [https://vcart-task.onrender.com/dashboard/](https://vcart-task.onrender.com/dashboard/) | Staff / Admin Only |
| **Django Admin Panel** | [https://vcart-task.onrender.com/admin/](https://vcart-task.onrender.com/admin/) | Staff / Superuser Only |

---

## 🔐 Credentials (Placeholders)

### Administrator Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@vcart.store`
- *Access Level:* Full Superuser & Staff privileges (accesses both `/admin/` and `/dashboard/`).

### Test Customer Account
- **Username:** `testuser` *(or `YOUR_TEST_USERNAME`)*
- **Password:** `TestUser123!` *(or `YOUR_TEST_PASSWORD`)*
- **Email:** `testuser@vcart.store`
- *Access Level:* Standard customer (store browsing, cart, profile management). Automatically created by the `seed_data` command.

---

## ⚡ Accessing the Dedicated Operations Dashboard

In addition to Django's standard backend at `/admin/`, Vcart features a custom-built, modern **Operations Dashboard** located at:

```
/dashboard/
```

### How Admins Access the Dashboard:
1. Log in with your **Admin / Staff** credentials via either:
   - Storefront login page: `/accounts/login/`
   - Standard Django login page: `/admin/login/`
2. Once authenticated as a staff member, a **"Dashboard"** link and icon automatically appear in the top storefront navigation bar.
3. You can also navigate directly to `/dashboard/` in your browser.
4. If a standard customer or unauthenticated visitor attempts to access `/dashboard/`, they are safely redirected to the login page (`@user_passes_test(is_staff_user)`).

### Why a Separate Dashboard?
- **Designed for Store Operations:** Tailored for daily catalog management without exposing technical Django settings or raw database internals.
- **Real-Time KPIs:** Live metric cards showing total products, active catalog items, disabled inventory, banner counts, and user metrics.
- **One-Click Toggles:** Instantly enable or disable products and banners directly from listing tables without opening edit forms.
- **Image Management:** Direct 1-click **"Remove Image Now"** action buttons and clearable file upload controls.
- **Direct System Link:** Includes a 1-click shortcut in the sidebar to jump directly into the technical `/admin/` panel whenever required.

---

## 🛠️ Technologies Used

- **Backend:** Python 3.12, Django 5.1 (MVT architecture, ModelForms, class/function views)
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom design tokens, CSS variables, glassmorphism, responsive flexbox & grid), Vanilla JavaScript (no heavy frontend frameworks required)
- **Image Generation & Processing:** Pillow (Python Imaging Library) for programmatic vector device illustration rendering
- **Static Asset Pipeline:** WhiteNoise with automatic gzip/Brotli compression and cache-busting manifest hashes
- **Media Asset Storage:** Cloudinary via `django-cloudinary-storage` (or persistent disk storage)
- **Database Engine:** SQLite (Local Dev) / PostgreSQL (Production on Render, Neon, Supabase, or AWS RDS)
- **Production Server:** Gunicorn WSGI HTTP Server

---

## 🗄️ Database Architecture

| Environment | Database | Driver / Configuration |
| :--- | :--- | :--- |
| **Development** | SQLite3 (`db.sqlite3`) | Standard `django.db.backends.sqlite3` |
| **Production** | Hosted PostgreSQL | Managed via `dj-database-url` and `psycopg2-binary` reading `DATABASE_URL` |

---

## 🚀 Major Features Implemented

### 1. Homepage & Storefront
- **Dynamic Hero Carousel / Banners:** Prominently displays active promotional hero banners with custom headline, subheading, and CTA button.
- **Interactive Category Browser:** Dynamic category tabs that filter store products smoothly.
- **Featured Products Section:** Highlights featured catalog items with badge indicators, pricing, and stock status.
- **Dynamic Promotional Callouts:** In-feed promotional cards directing customers to special sales.
- **Responsive Layout:** Optimized for mobile phones, tablets, laptops, and ultra-wide desktop displays.

### 2. Dynamic Banners
- **Full CRUD:** Create, view, edit, and delete banners through the Dashboard and Django Admin.
- **Live Activation Toggle:** Toggle banners between active and inactive states in real time.
- **Flexible Media:** Banners support uploaded high-resolution imagery or fallback gracefully to styled modern gradients if no image is attached.
- **Direct Redirection:** Custom CTA button text and destination URL fields.

### 3. Comprehensive Product Management
- **Full CRUD Support:** Complete creation, editing, listing, and deletion workflows.
- **Catalog Categorization:** Seamless association with parent product categories.
- **Inventory & Pricing:** Detailed price tracking, stock level counters, and low-stock alerts.
- **Optional Image Field:** Products support optional image uploads. When left blank, clean product illustration placeholders are automatically rendered.
- **Dual Image Deletion Controls:**
  - *Form Checkbox:* "Delete / clear current image" option inside the edit form.
  - *Direct 1-Click Action:* Direct `Remove Image Now` button on active product previews that purges the image immediately.
- **Quick Status Toggles:** Instantly toggle `is_active` and `is_featured` directly from the Dashboard table.

### 4. Product Details Page
- **High-Resolution Presentation:** Full-width image gallery with smooth aspect ratio containment.
- **Stock Indicators:** Dynamic in-stock / out-of-stock badge indicators.
- **Structured Specifications:** Full description formatting, pricing displays, and category navigation breadcrumbs.
- **Related Recommendations:** Automatically recommends related products in the same category.

### 5. Authentication & User Profile
- **User Registration:** Clean, validation-backed customer sign-up flow.
- **Session Authentication:** Secure login and CSRF-protected logout workflows.
- **Self-Service Customer Profile:** Allows registered users to view and update their first name, last name, and email address.
- **Permission Boundaries:** Strict server-side validation preventing non-staff users from accessing administrative tools.

### 6. Django Admin Panel (`/admin/`)
- Native Django administrative interface registered with customized `ModelAdmin` classes:
  - Custom list display columns, search fields, and category/status filters.
  - Image thumbnail previews inside table rows.
  - Bulk actions (e.g., **"Clear / remove image from selected products/banners"**).

### 7. Custom Operations Dashboard (`/dashboard/`)
- Protected by `@user_passes_test(is_staff_user)`.
- KPI summary metrics: Total Products, Active Catalog Items, Inactive Items, Total Categories, Active Banners, Total Registered Users, and Staff Accounts.
- Real-time product, category, banner, and user management tables with search and status filters.
- Dedicated user management interface to toggle staff privileges and account activity.

---

## 📦 Third-Party Libraries & Services

- **`Django` (5.1.x):** Core web framework.
- **`gunicorn` (>=21.2.0):** High-performance WSGI HTTP server for production.
- **`Pillow` (>=10.2.0):** Programmatic vector and raster image generation for seeded catalog items.
- **`whitenoise` (>=6.6.0):** Production static file serving and cache header optimization.
- **`dj-database-url` (>=2.1.0):** Twelve-factor database configuration parsing from `DATABASE_URL`.
- **`psycopg2-binary` (>=2.9.9):** High-performance PostgreSQL database adapter.
- **`cloudinary` & `django-cloudinary-storage`:** Cloud media asset hosting.
- **`python-dotenv` (>=1.0.0):** Local environment variable injection from `.env`.

---

## 💻 Local Setup Instructions

Follow these step-by-step instructions to run Vcart locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/vivekmenon2004/Vcart-Task-2.git
cd Vcart-Task-2
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root directory:

```env
SECRET_KEY=local-insecure-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

*(Optional: Add `DATABASE_URL` and `CLOUDINARY_URL` if you wish to test with external PostgreSQL or Cloudinary locally).*

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Populate Demo Data (Categories, Products, Banners, Test User)
Run the idempotent management command:
```bash
python manage.py seed_data
```
> **What this does:**
> - Creates 4 standard product categories (Phones, Laptops, Audio, Accessories).
> - Creates 10 products with descriptions, prices, stock levels, and generated placeholder illustrations.
> - Creates 3 dynamic promotional hero banners.
> - Creates the default test user (`testuser` / `TestUser123!`).

### 7. Create a Superuser / Admin
```bash
python manage.py createsuperuser
```
Follow the prompts to configure your administrator username, email, and password.

### 8. Run the Development Server
```bash
python manage.py runserver
```
Open your browser and visit:
- **Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Operations Dashboard:** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## ⚙️ Environment Variables Reference

When deploying to Render, Railway, or any production cloud environment, configure the following environment variables:

| Variable | Required in Prod | Description | Example Value |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | **Yes** | Django cryptographic signing key | `django-insecure-7!x...9a` *(Generate a strong random string)* |
| `DEBUG` | **Yes** | Toggle debug mode (`False` in production) | `False` |
| `DATABASE_URL` | **Yes** | Connection string for PostgreSQL database | `postgresql://user:password@host:5432/dbname` |
| `CLOUDINARY_URL` | Optional | Cloudinary credentials URL for uploaded images | `cloudinary://API_KEY:API_SECRET@CLOUD_NAME` |
| `ALLOWED_HOSTS` | Optional | Comma-separated list of allowed hostnames | `.onrender.com,localhost` |
| `CSRF_TRUSTED_ORIGINS` | Optional | Comma-separated trusted origins for CSRF | `https://*.onrender.com` |

---

## 🚀 Recommended Deployment: Render (render.com)

Render provides native, first-class support for Python, Django, Gunicorn, and PostgreSQL without serverless filesystem limitations or execution timeouts.

### Step-by-Step Render Deployment Guide:

1. **Create a Free PostgreSQL Database on Render:**
   - Log in to [render.com](https://render.com/).
   - Click **New +** > **PostgreSQL**.
   - Name it (e.g., `vcart-db`), choose your preferred region, and click **Create Database**.
   - Once provisioned, copy the **Internal Database URL** (or External Database URL).

2. **Deploy the Django Web Service:**
   - Click **New +** > **Web Service**.
   - Connect your GitHub repository: `vivekmenon2004/Vcart-Task-2`.
   - Configure the service settings:
     - **Name:** `vcart` (or your preferred name)
     - **Region:** Same region as your database
     - **Runtime:** `Python 3`
     - **Build Command:**
       ```bash
       pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
       ```
     - **Start Command:**
       ```bash
       gunicorn vcart.wsgi:application
       ```

3. **Configure Environment Variables in Render:**
   Under the **Environment** tab of your Render Web Service, add:
   - `SECRET_KEY` = `<a strong random secret string>`
   - `DEBUG` = `False`
   - `DATABASE_URL` = `<Paste the PostgreSQL URL copied from Step 1>`
   - `CLOUDINARY_URL` = `<Optional: your Cloudinary URL if using cloud media>`
   - `ALLOWED_HOSTS` = `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://*.onrender.com`

4. **Seed the Production Database & Create Admin:**
   Open the **Shell** tab on your deployed Render Web Service and run:
   ```bash
   python manage.py seed_data
   python manage.py createsuperuser
   ```

Your Vcart store is now fully deployed and live on the internet!

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
