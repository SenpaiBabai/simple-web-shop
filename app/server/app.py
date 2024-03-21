from fastapi import FastAPI,Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.responses import JSONResponse
app = FastAPI(title='Shop')
from app.server.product.product_rout import router as product_router
from app.server.user.user_rout import router as user_router
from app.server.basket.basket_rout import router as basket_router
from app.server.order.order_rout import router as order_router

# app = FastAPI(title='Shop')
app.include_router(user_router)
app.include_router(product_router)
app.include_router(basket_router)
app.include_router(order_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": 'Incorect data'}), )
