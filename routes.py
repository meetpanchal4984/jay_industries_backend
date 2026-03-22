from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import models, schemas, auth, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the email or mobile is already registered
        db_user = db.query(models.User).filter(
            (models.User.email == user.email) | (models.User.mobile == user.mobile)
        ).first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email or Mobile already registered"
            )
        
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
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # Since OAuth2PasswordRequestForm expects username and password, we assume username = email
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user or not auth.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Update login status
        user.is_logged_in = True
        db.commit()
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/contact")
def handle_contact(contact: schemas.ContactCreate):
    from email_utils import send_contact_email
    success = send_contact_email(
        name=contact.full_name,
        email=contact.email,
        phone=contact.phone,
        subject=contact.subject,
        message=contact.message
    )
    if not success:
        # We still return 200 but maybe with a warning or just log it
        # Actually, let's return a specific message
        return {"message": "Message received, but email notification failed. We will check it manually."}
    return {"message": "Your message has been sent successfully!"}
