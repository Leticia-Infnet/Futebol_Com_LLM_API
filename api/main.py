from fastapi import FastAPI
from routers.match_summary import router as match_summary_router
from routers.player_profile import router as player_profile_router

app = FastAPI()

app.include_router(match_summary_router,
                   prefix='/summary', tags=['summary'])

app.include_router(player_profile_router,
                   prefix='/profile', tags=['profile'])


@app.get('/')
def read_root():
    return {'message': 'O servirdor está no ar!'}
