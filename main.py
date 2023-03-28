import asyncio

from app.api import ReportCreator

if __name__ == '__main__':
    asyncio.run(ReportCreator().connect(sleep=False))
