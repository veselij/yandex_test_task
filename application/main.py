from fastapi import FastAPI, Request, status
from routes.couriers import router as courier_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from routes.orders import router as order_router
from fastapi.openapi.utils import get_openapi


app = FastAPI()
app.include_router(courier_router, prefix='/couriers')
app.include_router(order_router,  prefix='/orders')


@app.get('/')
async def read_root():
    return {'message': 'Candy Delivery API'}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if isinstance(exc.body, dict) and 'data' in exc.body.keys():
        bad_ids = []
        uniq_errs = []
        for err in exc.errors():
            print(err)
            data = exc.body['data'][err['loc'][2]]
            id = [k.replace('_id', '') for k in data.keys() if k.endswith('_id')][0]
            bad_ids.append({'id': data[f'{id}_id']})
            uniq_errs.append(err['type']) if err['type'] not in uniq_errs else uniq_errs
        if 'value_error.extra' in uniq_errs or 'value_error.missing' in uniq_errs:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({"validation_error": {f"{id}s": bad_ids}}),
        )
        else:
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),)
    else:
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),)


def del_openapi_redundunt_elements(openaip):
    if isinstance(openaip, dict):
        for key in list(openaip.keys()):
            if key in ['422', 'summary', 'operationId', 'HTTPValidationError', 'ValidationError']:
                del openaip[key]
            else:
                del_openapi_redundunt_elements(openaip[key])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Candy Delivery App",
        version="1.0",
        routes=app.routes,
    )
    del_openapi_redundunt_elements(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
