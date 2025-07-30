"""
Image generation examples for LangChain DeepAI integration.

This script demonstrates the image generation capabilities.
"""

import os
from langchain_deepai import ImageDeepAI, generate_image

def basic_image_generation():
    """Basic image generation example."""
    print("=== Basic Image Generation ===")
    
    # Initialize image generator
    image_gen = ImageDeepAI()
    
    # Generate a simple image
    result = image_gen.generate(
        prompt="A beautiful sunset over mountains with a lake reflection",
        model="text2img"
    )
    
    # Save the image
    with open("sunset_mountains.jpg", "wb") as f:
        f.write(result["image_data"])
    
    print(f"Image generated and saved to: sunset_mountains.jpg")
    print(f"Image URL: {result['image_url']}")
    print(f"Metadata: {result['metadata']}")


def different_styles_example():
    """Examples using different artistic styles."""
    print("\n=== Different Artistic Styles ===")
    
    image_gen = ImageDeepAI()
    
    # Different style examples
    examples = [
        {
            "prompt": "A majestic dragon in a medieval castle",
            "model": "fantasy-world-generator",
            "filename": "fantasy_dragon.jpg"
        },
        {
            "prompt": "A futuristic city with flying cars and neon lights",
            "model": "cyberpunk-generator", 
            "filename": "cyberpunk_city.jpg"
        },
        {
            "prompt": "A peaceful garden with flowers and butterflies",
            "model": "impressionism-painting-generator",
            "filename": "impressionist_garden.jpg"
        },
        {
            "prompt": "An abstract representation of music and emotion",
            "model": "abstract-painting-generator",
            "filename": "abstract_music.jpg"
        }
    ]
    
    for example in examples:
        try:
            print(f"Generating: {example['prompt'][:50]}...")
            result = image_gen.generate_and_save(
                prompt=example["prompt"],
                filepath=example["filename"],
                model=example["model"]
            )
            print(f"✓ Saved to: {example['filename']}")
        except Exception as e:
            print(f"✗ Failed: {e}")


def batch_generation_example():
    """Example of generating multiple images at once."""
    print("\n=== Batch Generation ===")
    
    image_gen = ImageDeepAI()
    
    prompts = [
        "A serene lake at sunrise",
        "A bustling city street at night",
        "A peaceful forest in autumn",
        "A snow-covered mountain peak"
    ]
    
    print(f"Generating {len(prompts)} images...")
    results = image_gen.generate_multiple(prompts, model="text2img")
    
    for i, result in enumerate(results):
        if "error" not in result:
            filename = f"batch_image_{i+1}.jpg"
            with open(filename, "wb") as f:
                f.write(result["image_data"])
            print(f"✓ Image {i+1} saved to: {filename}")
        else:
            print(f"✗ Image {i+1} failed: {result['error']}")


def convenience_function_example():
    """Example using the convenience function."""
    print("\n=== Convenience Function ===")
    
    # Using the generate_image convenience function
    result = generate_image(
        prompt="A lighthouse on a rocky coast during a storm",
        model="text2img",
        width=512,
        height=512
    )
    
    # Save the image
    with open("lighthouse_storm.jpg", "wb") as f:
        f.write(result["image_data"])
    
    print("Image generated using convenience function!")
    print(f"Saved to: lighthouse_storm.jpg")


def model_information_example():
    """Example showing available image models."""
    print("\n=== Available Image Models ===")
    
    image_gen = ImageDeepAI()
    models = image_gen.get_available_models()
    
    print("Available Image Generation Models:")
    for model_name, info in models.items():
        print(f"\n{model_name}:")
        print(f"  Description: {info['description']}")
        print(f"  Best for: {info['best_for']}")
        print(f"  Style: {info['style']}")


def advanced_parameters_example():
    """Example with advanced parameters."""
    print("\n=== Advanced Parameters ===")
    
    image_gen = ImageDeepAI()
    
    # Generate with specific dimensions (if supported)
    result = image_gen.generate(
        prompt="A detailed portrait of a wise old wizard",
        model="fantasy-world-generator",
        width=768,
        height=768,
        # Additional parameters can be added here
    )
    
    with open("wizard_portrait.jpg", "wb") as f:
        f.write(result["image_data"])
    
    print("High-resolution wizard portrait generated!")
    print(f"Metadata: {result['metadata']}")


def main():
    """Run all image generation examples."""
    print("LangChain DeepAI - Image Generation Examples")
    print("=" * 50)
    
    try:
        basic_image_generation()
        different_styles_example()
        batch_generation_example()
        convenience_function_example()
        model_information_example()
        advanced_parameters_example()
        
        print("\n" + "=" * 50)
        print("All image generation examples completed!")
        print("Check the generated image files in the current directory.")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set your DEEPAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
