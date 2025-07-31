import base64
import json
import time
from typing import List, Optional, Union

import requests

from markdown_html_pdf._constants import api_keys

# Fireworks API configuration
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/completions"


class FireworksLLMs:
    # Meta Llama 4 models
    llama4_scout_instruct_basic = "accounts/fireworks/models/llama4-scout-instruct-basic"
    llama4_maverick_instruct_basic = "accounts/fireworks/models/llama4-maverick-instruct-basic"
    # Alibaba Qwen models
    qwen3_235b_a22b_thinking_2507 = "accounts/fireworks/models/qwen3-235b-a22b-thinking-2507"
    qwen3_coder_480b_a35b_instruct = "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct"
    qwen3_235b_a22b_instruct_2507 = "accounts/fireworks/models/qwen3-235b-a22b-instruct-2507"
    # Moonshot AI Kimi models
    kimi_k2_instruct = "accounts/fireworks/models/kimi-k2-instruct"
    # DeepSeek models
    deepseek_v3_0324 = "accounts/fireworks/models/deepseek-v3-0324"
    deepseek_r1_0528 = "accounts/fireworks/models/deepseek-r1-0528"


def call_fireworks_llm_requests(
    model: str,
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1024,
    top_p: float = 1,
    top_k: int = 40,
    presence_penalty: float = 0,
    frequency_penalty: float = 0,
    stop: str = None,
    images: Optional[List[Union[str, bytes]]] = None,
) -> str:
    """
    Call Fireworks LLM API using requests with support for text and images.

    Args:
        model: The model name to use
        prompt: The text prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens to generate
        top_p: Controls diversity via nucleus sampling
        top_k: Controls diversity via top-k sampling
        presence_penalty: Penalty for presence of tokens
        frequency_penalty: Penalty for frequency of tokens
        stop: Stop sequence
        images: Optional list of images (URLs, file paths, or base64 encoded data)

    Returns:
        The generated response text
    """
    if not api_keys.FIREWORKS_API_KEY:
        raise ValueError("FIREWORKS_API_KEY is required")

    # Measure time
    start_time = time.time()

    # Prepare payload
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "temperature": temperature,
        "prompt": prompt,
    }

    # Add stop sequence if provided
    if stop:
        payload["stop"] = stop

    # Add images if provided
    if images:
        payload["images"] = []
        for image in images:
            if isinstance(image, str):
                if image.startswith("http"):
                    # URL image
                    payload["images"].append(image)
                elif image.startswith("data:image"):
                    # Base64 data URL
                    payload["images"].append(image)
                else:
                    # File path
                    try:
                        with open(image, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode()
                        # Detect image format
                        image_format = "jpeg"
                        if image.lower().endswith(".png"):
                            image_format = "png"
                        elif image.lower().endswith(".gif"):
                            image_format = "gif"
                        elif image.lower().endswith(".webp"):
                            image_format = "webp"

                        data_url = f"data:image/{image_format};base64,{image_data}"
                        payload["images"].append(data_url)
                    except Exception as e:
                        print(f"Error reading image file {image}: {e}")
            elif isinstance(image, bytes):
                # Raw bytes (assume JPEG)
                image_data = base64.b64encode(image).decode()
                data_url = f"data:image/jpeg;base64,{image_data}"
                payload["images"].append(data_url)

    # Prepare headers
    headers = {"Authorization": f"Bearer {api_keys.FIREWORKS_API_KEY}", "Content-Type": "application/json"}

    # Make request
    response = requests.post(FIREWORKS_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        raise Exception(f"Fireworks API error: {response.status_code} - {response.text}")

    # Parse response
    result = response.json()

    # Measure time
    end_time = time.time()
    print(f"⚡ Time taken to call Fireworks LLM ({model}): {end_time - start_time} seconds")

    return result["choices"][0]["text"]


def call_fireworks_llm_sdk(
    model: str,
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1024,
    top_p: float = 1,
    top_k: int = 40,
    presence_penalty: float = 0,
    frequency_penalty: float = 0,
    stop: str = None,
    images: Optional[List[Union[str, bytes]]] = None,
) -> str:
    """
    Call Fireworks LLM API using the Fireworks SDK with support for text and images.

    Args:
        model: The model name to use (without 'accounts/fireworks/models/' prefix)
        prompt: The text prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens to generate
        top_p: Controls diversity via nucleus sampling
        top_k: Controls diversity via top-k sampling
        presence_penalty: Penalty for presence of tokens
        frequency_penalty: Penalty for frequency of tokens
        stop: Stop sequence
        images: Optional list of images (URLs, file paths, or base64 encoded data)

    Returns:
        The generated response text
    """
    try:
        from fireworks import LLM
    except ImportError:
        raise ImportError("Fireworks SDK not installed. Install with: pip install fireworks")

    if not api_keys.FIREWORKS_API_KEY:
        raise ValueError("FIREWORKS_API_KEY is required")

    # Measure time
    start_time = time.time()

    # Initialize LLM
    llm = LLM(model=model, deployment_type="auto")

    # Prepare message content
    message_content = [{"type": "text", "text": prompt}]

    # Add images if provided
    if images:
        for image in images:
            if isinstance(image, str):
                if image.startswith("http"):
                    # URL image
                    message_content.append({"type": "image_url", "image_url": {"url": image}})
                elif image.startswith("data:image"):
                    # Base64 data URL
                    message_content.append({"type": "image_url", "image_url": {"url": image}})
                else:
                    # File path
                    try:
                        with open(image, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode()
                        # Detect image format
                        image_format = "jpeg"
                        if image.lower().endswith(".png"):
                            image_format = "png"
                        elif image.lower().endswith(".gif"):
                            image_format = "gif"
                        elif image.lower().endswith(".webp"):
                            image_format = "webp"

                        data_url = f"data:image/{image_format};base64,{image_data}"
                        message_content.append({"type": "image_url", "image_url": {"url": data_url}})
                    except Exception as e:
                        print(f"Error reading image file {image}: {e}")
            elif isinstance(image, bytes):
                # Raw bytes (assume JPEG)
                image_data = base64.b64encode(image).decode()
                data_url = f"data:image/jpeg;base64,{image_data}"
                message_content.append({"type": "image_url", "image_url": {"url": data_url}})

    # Call LLM
    response = llm.chat.completions.create(
        messages=[{"role": "user", "content": message_content}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        top_k=top_k,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        stop=stop,
    )

    # Measure time
    end_time = time.time()
    print(f"⚡ Time taken to call Fireworks LLM SDK ({model}): {end_time - start_time} seconds")

    return response.choices[0].message.content


# Convenience function that uses SDK by default
def call_fireworks_llm(
    model: str,
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 1024,
    top_p: float = 1,
    top_k: int = 40,
    presence_penalty: float = 0,
    frequency_penalty: float = 0,
    stop: str = None,
    images: Optional[List[Union[str, bytes]]] = None,
    use_sdk: bool = True,
) -> str:
    """
    Call Fireworks LLM API with support for text and images.
    Uses SDK by default, falls back to requests if SDK is not available.

    Args:
        model: The model name to use
        prompt: The text prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens to generate
        top_p: Controls diversity via nucleus sampling
        top_k: Controls diversity via top-k sampling
        presence_penalty: Penalty for presence of tokens
        frequency_penalty: Penalty for frequency of tokens
        stop: Stop sequence
        images: Optional list of images (URLs, file paths, or base64 encoded data)
        use_sdk: Whether to use the Fireworks SDK (True) or requests (False)

    Returns:
        The generated response text
    """
    if use_sdk:
        try:
            return call_fireworks_llm_sdk(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stop=stop,
                images=images,
            )
        except ImportError:
            print("Fireworks SDK not available, falling back to requests API")
            return call_fireworks_llm_requests(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                stop=stop,
                images=images,
            )
    else:
        return call_fireworks_llm_requests(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            stop=stop,
            images=images,
        )
