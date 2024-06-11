from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from decouple import config
from pickle import load
import googleapiclient.discovery as gapi
from pandas import Series
from numpy import count_nonzero
from textblob import TextBlob
import os


async def get_comments(youtube, video_id):
    comment_text = []
    results = (
        youtube.commentThreads()
        .list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100,
            order="relevance",
        )
        .execute()
    )
    for i in range(len(results["items"])):
        d = dict(results["items"][i])
        d1 = d["snippet"]
        d2 = d1["topLevelComment"]
        d3 = d2["snippet"]
        comment_text.append(d3["textDisplay"])
    while len(results) == 5:
        results = (
            youtube.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                order="relevance",
                pageToken=results["nextPageToken"],
            )
            .execute()
        )
        for i in range(len(results["items"])):
            d = dict(results["items"][i])
            d1 = dict(d["snippet"])
            d2 = dict(d1["topLevelComment"])
            d3 = dict(d2["snippet"])
            comment_text.append(d3["textDisplay"])
    return comment_text


async def calculating_sentiment(comment_text, m, v):
    model = m
    vect = v
    comments = Series(comment_text)
    comm = vect.transform(comments)
    res = model.predict(comm)
    pos = count_nonzero(res == "4")
    neg = count_nonzero(res == "0")
    return pos, neg


async def calculating_sentiment_textblob(comments):
    pos = 0
    neg = 0
    neutral = 0
    for c in comments:
        s = float(TextBlob(c).sentiment.polarity)
        if s > 0:
            pos += 1
        elif s < 0:
            neg += 1
        else:
            neutral += 1

    return pos, neg, neutral


API_KEY = config("KEY")

video = APIRouter()
youtube = gapi.build("youtube", "v3", developerKey=API_KEY)


class VideoID(BaseModel):
    id: str = Field(...)

    class Config:
        schema_extra = {"id": "b5F667g1yCk"}


model = None
vect = None
model_path = os.path.join(os.getcwd(), "router/model.pkl")
with open(model_path, "rb") as f:
    model = load(f)
vect_path = os.path.join(os.getcwd(), "router/vect.pkl")
with open(vect_path, "rb") as v:
    vect = load(v)


@video.post("/mymodel")
async def get_Sentiment(vid: VideoID):
    """
    Calculate sentiment for a given video using my trained model.<br>
    MAX 2000 top comments.
    """
    comments = None
    # print(vid.id)
    try:
        comments = await get_comments(youtube, vid.id.strip())
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Video ID incorrect. Please request again with proper video ID.",
        )
    print(len(comments))
    # print(type(comments))
    pos, neg = await calculating_sentiment(comments, model, vect)
    # print(pos)
    # print(neg)
    return {"pos": pos, "neg": neg}


@video.post("/textblob")
async def get_Sentiment_with_Textblob(vid: VideoID):
    """
    Calculate sentiment for a given video using Textblob sentiment analyser.<br>
    MAX 2000 top comments.
    """
    comments = None
    # print(vid.id)
    try:
        comments = await get_comments(youtube, vid.id.strip())
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Video ID incorrect. Please request again with proper video ID.",
        )
    print(len(comments))
    # print(type(comments))
    pos, neg, neutral = await calculating_sentiment_textblob(comments)
    # print(pos)
    # print(neg)
    # print(neutral)
    return {"pos": pos, "neg": neg, "neutral": neutral}
