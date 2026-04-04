from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import models, schemas, auth, database
from storage import upload_image, delete_image

router = APIRouter()

from database import get_db

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(
            (models.User.email == user.email) | (models.User.mobile == user.mobile)
        ).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email or Mobile already registered")
        
        hashed_password = auth.get_password_hash(user.password)
        new_user = models.User(
            full_name=user.full_name,
            email=user.email,
            mobile=user.mobile,
            hashed_password=hashed_password,
            is_registered=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        user.is_logged_in = True
        db.commit()
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/contact")
async def handle_contact(contact: schemas.ContactCreate):
    from email_utils import send_contact_email
    success = await send_contact_email(
        name=contact.full_name,
        email=contact.email,
        phone=contact.phone,
        subject=contact.subject,
        message=contact.message
    )
    if not success:
        return {"message": "Message received, but email notification failed."}
    return {"message": "Your message has been sent successfully!"}

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.get("/admin/stats", response_model=schemas.DashboardStats)
def get_admin_stats(current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    logged_in_users = db.query(models.User).filter(models.User.is_logged_in == True).count()
    return {
        "total_users": total_users,
        "logged_in_users": logged_in_users,
        "active_users": logged_in_users
    }

@router.get("/admin/users", response_model=list[schemas.UserResponse])
def get_admin_users(current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.is_published == True).all()

@router.get("/admin/products", response_model=List[schemas.ProductResponse])
def get_admin_products(current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.get("/admin/dashboard-data", response_model=schemas.AdminDashboardData)
def get_admin_dashboard_data(current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    # Fetch stats
    total_users = db.query(models.User).count()
    logged_in_users = db.query(models.User).filter(models.User.is_logged_in == True).count()
    
    # Fetch users
    users = db.query(models.User).all()
    
    # Fetch products
    products = db.query(models.Product).all()
    
    return {
        "stats": {
            "total_users": total_users,
            "logged_in_users": logged_in_users,
            "active_users": logged_in_users
        },
        "users": users,
        "products": products
    }

@router.put("/admin/products/{product_id}/toggle-publish", response_model=schemas.ProductResponse)
def toggle_product_publish(product_id: int, current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_published = not product.is_published
    db.commit()
    db.refresh(product)
    return product

@router.delete("/admin/products/{product_id}")
async def delete_product(product_id: int, current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete main image from Supabase
    if product.image_url.startswith("http"):
        await delete_image(product.image_url)
    elif product.image_url.startswith("/static/"):
        import os
        path = product.image_url.lstrip("/")
        if os.path.exists(path):
            os.remove(path)
            
    # Delete sub-images from Supabase
    for img in product.sub_images:
        if img.image_url.startswith("http"):
            await delete_image(img.image_url)
        elif img.image_url.startswith("/static/"):
            import os
            path = img.image_url.lstrip("/")
            if os.path.exists(path):
                os.remove(path)
                
    db.delete(product)
    db.commit()
    return {"message": "Product and associated images deleted successfully!"}

@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products", response_model=schemas.ProductResponse)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    main_image: UploadFile = File(...),
    sub_images: List[UploadFile] = File([]),
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        # Save main image to Supabase
        main_image_content = await main_image.read()
        main_image_url = await upload_image(main_image_content, main_image.filename)
        
        # Create product
        new_product = models.Product(
            name=name,
            description=description,
            image_url=main_image_url
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Save sub-images to Supabase
        for img in sub_images:
            if img.filename:
                s_content = await img.read()
                s_url = await upload_image(s_content, img.filename)
                db_img = models.ProductImage(product_id=new_product.id, image_url=s_url)
                db.add(db_img)
        
        db.commit()
        db.refresh(new_product)
        return new_product
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Product Create Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@router.post("/logout")
def logout(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Fetch the user in the current session to ensure the update is recorded
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if db_user:
        db_user.is_logged_in = False
        db.commit()
    return {"message": "Logged out successfully"}

@router.put("/admin/users/{user_id}/toggle-admin", response_model=schemas.UserResponse)
def toggle_admin_status(user_id: int, current_user: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="For safety, you cannot revoke your own administrator status.")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return user
