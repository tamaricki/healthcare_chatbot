
import asyncio 

#to resolve intermittent connection issues with Neo4j, you should try establishing connection again. 
# below is retry function that works for asyncronous functions

def async_retry(max_retries: int=3, delay: int=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries+1):
                try:
                    result= await func( *args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Attempt {attempt} failed: {str(e)}")
                    await asyncio.sleep(delay)
            raise ValueError(f"Falied after {max_retries} attempts.")

        return wrapper
    return decorator 