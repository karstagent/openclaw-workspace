import logging
from typing import List, Dict

class ModelRotationStrategy:
    def __init__(self):
        self.models = {
            'haiku': {
                'name': 'Claude Haiku',
                'provider': 'openrouter/anthropic/claude-3.5-haiku',
                'complexity': 'low-medium',
                'token_efficiency': 'high'
            },
            'sonnet': {
                'name': 'Claude Sonnet',
                'provider': 'openrouter/anthropic/claude-3.7-sonnet',
                'complexity': 'medium-high',
                'token_efficiency': 'moderate'
            },
            'deepseek': {
                'name': 'DeepSeek',
                'provider': 'openrouter/deepseek/deepseek-coder',
                'complexity': 'administrative',
                'token_efficiency': 'very high'
            }
        }
        
        # Logging setup
        logging.basicConfig(
            filename='/tmp/model_rotation.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    def select_model(self, task_complexity: Dict[str, str]) -> str:
        """
        Dynamically select the most appropriate model
        
        Task Complexity Dimensions:
        - reasoning_depth: shallow, moderate, deep
        - context_requirements: minimal, moderate, extensive
        - output_creativity: low, medium, high
        """
        reasoning = task_complexity.get('reasoning_depth', 'shallow')
        context = task_complexity.get('context_requirements', 'minimal')
        creativity = task_complexity.get('output_creativity', 'low')

        if reasoning == 'shallow' and context == 'minimal':
            return 'deepseek'
        elif reasoning in ['shallow', 'moderate'] and context in ['minimal', 'moderate']:
            return 'haiku'
        else:
            return 'sonnet'

    def get_model_details(self, model_key: str) -> Dict:
        """
        Retrieve detailed model information
        """
        return self.models.get(model_key, {})

# Example usage
def main():
    strategy = ModelRotationStrategy()
    
    # Example tasks with varying complexity
    tasks = [
        {
            'description': 'Simple data entry',
            'complexity': {
                'reasoning_depth': 'shallow',
                'context_requirements': 'minimal',
                'output_creativity': 'low'
            }
        },
        {
            'description': 'Research summary',
            'complexity': {
                'reasoning_depth': 'moderate',
                'context_requirements': 'moderate',
                'output_creativity': 'medium'
            }
        },
        {
            'description': 'Strategic business analysis',
            'complexity': {
                'reasoning_depth': 'deep',
                'context_requirements': 'extensive',
                'output_creativity': 'high'
            }
        }
    ]
    
    # Process and log model selections
    for task in tasks:
        selected_model = strategy.select_model(task['complexity'])
        model_details = strategy.get_model_details(selected_model)
        
        print(f"Task: {task['description']}")
        print(f"Selected Model: {model_details['name']}")
        print(f"Model Provider: {model_details['provider']}\n")

if __name__ == "__main__":
    main()