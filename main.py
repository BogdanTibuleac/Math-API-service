from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
import math, logging
from functools import lru_cache
import uvicorn
import redis
import os
from concurrent.futures import ThreadPoolExecutor

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

# ======================= CONFIG & INIT =======================
DATABASE_URL = "sqlite:///./data/math_service.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Math Operations API")
logger = logging.getLogger("math_service")
logging.basicConfig(level=logging.INFO)

executor = ThreadPoolExecutor(max_workers=4)
#http://localhost:8501/


# ======================= MODELS =======================
class OperationLog(Base):
    __tablename__ = "operation_logs"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, index=True)
    input_value = Column(String)
    result = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ======================= SCHEMAS =======================
class OperationRequest(BaseModel):
    value: int
    exponent: int | None = None

class OperationResponse(BaseModel):
    operation: str
    input_value: str
    result: float

# ======================= DB DEPENDENCY =======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================= CONTROLLERS =======================
class MathService:
    def __init__(self, db: Session):
        self.db = db

    def log_operation(self, op: str, input_val: str, result: float):
        log_entry = OperationLog(operation=op, input_value=input_val, result=result)
        self.db.add(log_entry)
        self.db.commit()
        logger.info(f"Logged operation: {op}({input_val}) = {result}")

    def power(self, base: int, exponent: int) -> float:
        result = math.pow(base, exponent)
        self.log_operation("power", f"{base}^{exponent}", result)
        return result

    @lru_cache(maxsize=128)
    def fibonacci(self, n: int) -> float:
        if n < 0:
            raise ValueError("Fibonacci number cannot be negative")

        cached = redis_client.get(f"fib:{n}")
        if cached:
            return float(cached)

        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b

        result = float(a)
        redis_client.set(f"fib:{n}", result, ex=3600)  # cache for 1 hour
        self.log_operation("fibonacci", str(n), result)
        return result

    def big_factorial(self, n: int) -> int:
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    def factorial(self, n: int) -> float:
        if n < 0:
            raise ValueError("Factorial input must be non-negative")
        if n > 5000:
            raise ValueError("Value too large. Try a number <= 5000")

        future = executor.submit(self.big_factorial, n)
        result = future.result(timeout=10)
        self.log_operation("factorial", str(n), float(result))
        return float(result)

# ======================= ROUTES =======================
@app.get("/")
async def read_root():
    return {"message": "Math API is running. Visit /docs for Swagger UI."}

@app.post("/api/power", response_model=OperationResponse)
async def compute_power(req: OperationRequest, db: Session = Depends(get_db)):
    if req.exponent is None:
        raise HTTPException(status_code=400, detail="Exponent is required for power computation")
    service = MathService(db)
    result = service.power(req.value, req.exponent)
    return OperationResponse(operation="power", input_value=f"{req.value}^{req.exponent}", result=result)

@app.post("/api/fibonacci", response_model=OperationResponse)
async def compute_fibonacci(req: OperationRequest, db: Session = Depends(get_db)):
    service = MathService(db)
    result = service.fibonacci(req.value)
    return OperationResponse(operation="fibonacci", input_value=str(req.value), result=result)

    service = MathService(db)
    try:
        result = service.factorial(req.value)
        return OperationResponse(operation="factorial", input_value=str(req.value), result=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
@app.post("/api/factorial", response_model=OperationResponse)
async def compute_factorial(req: OperationRequest, db: Session = Depends(get_db)):
    service = MathService(db)
    try:
        result = service.factorial(req.value)
        return OperationResponse(operation="factorial", input_value=str(req.value), result=result)
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Unexpected error during factorial computation")
        raise HTTPException(status_code=500, detail="Internal server error")

# ======================= ENTRY POINT =======================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)