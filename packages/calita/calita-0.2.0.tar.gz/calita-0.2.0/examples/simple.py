from calita.manager_agent import ManagerAgent
from calita.utils import get_global_config

if __name__ == "__main__":
    # Load configuration
    config = get_global_config("config.yaml")

    # Initialize the agent
    manager = ManagerAgent(config)

    # Process a task
    result = manager.orchestrate("Create a function to sort a list of numbers")
    print(result)
    # result = manager.orchestrate("本周黄金走势")
    # print(result)
    #result = manager.orchestrate("中间件故障解决方案，faultCode=F03, severity=2")
    #print(result)