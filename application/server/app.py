from fastapi import FastAPI, Request, status
from server.routes.couriers import router as courier_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from server.models.couriers import CourierSchema
from server.routes.orders import router as order_router


app = FastAPI()
app.include_router(courier_router, tags=['couriers'], prefix='/couriers')
app.include_router(order_router, tags=['orders'], prefix='/orders')

@app.get('/')
async def read_root():
    return {'message': 'Hello word!'}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if isinstance(exc.body, dict) and 'data' in exc.body.keys():
        bad_ids = []
        for err in exc.errors():
            data = exc.body['data'][err['loc'][2]]
            id = [k.replace('_id', '') for k in data.keys() if k.endswith('_id')][0]
            bad_ids.append({'id': data[f'{id}_id']})
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"validation_error": {f"{id}s": bad_ids}}),
        )
    else:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),)
