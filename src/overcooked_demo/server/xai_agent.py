import random

agent_types = ["NoX", "StaticX", "AdaX"]
target_counts = {"NoX": 6, "StaticX": 7, "AdaX": 7}

fallback_order = [['NoX', 'AdaX', 'AdaX', 'StaticX'], ['AdaX', 'AdaX', 'StaticX', 'NoX'], ['StaticX', 'AdaX', 'NoX', 'AdaX'], ['NoX', 'AdaX', 'StaticX', 'StaticX'], ['NoX', 'StaticX', 'StaticX', 'NoX']]
# Helper to count current assignments
current_counts = {"NoX": 0, "StaticX": 0, "AdaX": 0}

def select_double_agent():
    # Prioritize AdaX, then StaticX for double assignment if still under target
    priorities = ["AdaX", "StaticX", "NoX"]
    for agent in priorities:
        if current_counts[agent] + 2 <= target_counts[agent]:
            return agent
    return None  # fallback if all at limit

def assignXAIAgents():
    print("Creating XAI agent assignment...")
    sessions = []
    double_agent = None
    for _ in range(5):
        trial = 0
        while trial < 3: 
            print(trial)
            double_agent = select_double_agent()
            trial+=1
            if not double_agent:
                # try again
                print("[XAI] Retrying. No agent can be doubled without violating target counts.")
                continue
            else:
                break
            
        
        if not double_agent:
            print("[XAI] Trials failed. No agent can be doubled without violating target counts.")

        session = [double_agent, double_agent]
        others = [a for a in agent_types if a != double_agent]
        for a in others:
            if current_counts[a] < target_counts[a]:
                session.append(a)
            else:
                # fallback: add any other agent below target
                alt = next(agent for agent in agent_types if agent != double_agent and current_counts[agent] < target_counts[agent])
                session.append(alt)

        random.shuffle(session)
        for a in session:
            current_counts[a] += 1
        sessions.append(session)
        
    return sessions
