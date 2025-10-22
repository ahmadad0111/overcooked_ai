import os
import torch
# from modules.agents import HiPPOAgent
from modules.agents import HiPPOAgent, HiAgent, LoAgent, CNNAgent
#from agents import HiPPOAgent, HiAgent, LoAgent, CNNAgent


def load_model_state(agent, agent_name, path):
    """Load trained model weights (with optimizer if available)."""
    ckpt_path = os.path.join(path, f"{agent_name}_model.pt")
    checkpoint = torch.load(ckpt_path, map_location=torch.device("cpu"))
    
    agent.load_state_dict(checkpoint["model_state_dict"])
    print(f"Loaded {agent_name} model from {ckpt_path}")

    return agent


def load(agent, agent_name, path):
    """Load only model weights (no optimizer)."""
    model_path = os.path.join(path, f"{agent_name}.pt")
    agent.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    print(f"Loaded weights from {model_path}")
    return agent


def load_model_state_pasd(agent_hi, agent_lo,agent_name,path):

    ckpt_path = os.path.join(path, f"{agent_name}_model.pt")

    print(ckpt_path)
    checkpoint = torch.load(ckpt_path, map_location=torch.device("cpu"))


    agent_lo.load_state_dict(checkpoint['lo_model_state_dict'])


    agent_hi.load_state_dict(checkpoint['hi_model_state_dict'])
    return agent_hi, agent_lo


def infer_pop(agent_name="cramped_room", path="./modules/pop_trained/", obs_shape = [26,5,4],z_dim = 6):
    """Initialize and load trained HiPPO agent for inference."""
    # obs_shape = [26, 5, 4]
    # z_dim = 6
    agent = CNNAgent(obs_shape)

    # Load checkpoint
    agent= load_model_state(agent, agent_name, path)

    # Set to eval mode
    agent.eval()
 
    return agent


def infer_hipt(agent_name="cramped_room", path="./modules/hipt_trained/", obs_shape = [26,5,4],z_dim = 6):
    """Initialize and load trained HiPPO agent for inference."""
    # obs_shape = [26, 5, 4]
    # z_dim = 6
    agent = HiPPOAgent(obs_shape, z_dim)

    # Load checkpoint
    agent= load_model_state(agent, agent_name, path)

    # Set to eval mode
    agent.eval()
 
    return agent

def infer_pasd(agent_name="cramped_room", path="./modules/pasd_trained/", obs_shape= [26,5,4], z_dim= 6):
    """Initialize and load trained PASD agent for inference."""
    # obs_shape = [26, 5, 4]
    # z_dim = 6
    agent_hi = HiAgent(obs_shape, z_dim)
    agent_lo = LoAgent(obs_shape,z_dim)

    # Load checkpoint

    agent_hi, agent_lo = load_model_state_pasd(agent_hi, agent_lo,agent_name,path)

    # Set to eval mode
    agent_hi.eval()
    agent_lo.eval()

    return agent_hi, agent_lo

if __name__ == "__main__":
    agent_type = 'pasd'
    agent_name="PPOCounterCircuit"
    obs_shape= [26,8,5]
    z_dim= 6

    if agent_type == 'hipt':
        print("hipt agent!")
        agent = infer_hipt(agent_name="cramped_room")
        lstm_state = (
        torch.zeros(agent.lstm.num_layers, 1, agent.lstm.hidden_size),
        torch.zeros(agent.lstm.num_layers, 1, agent.lstm.hidden_size),)   
        next_done = torch.zeros(1)


        # Example dummy observation (adjust shape as needed)
        agent_obs = torch.randn(1, 26, 5, 4)
        with torch.no_grad():
            current_lstm_state = (lstm_state[0].clone(), lstm_state[1].clone())

            z, _, ent, ___, lstm_state, ____ = agent.get_z_and_value(agent_obs, next_done, lstm_state)
            agent_actions, _, __, ___, _____, ______ = agent.get_action_and_value(agent_obs, z, next_done, current_lstm_state)
            print("Predicted action:", agent_actions)


    elif agent_type == 'pasd':
        print("pasd agent!")
        agent_hi, agent_lo =  infer_pasd(agent_name=agent_name, obs_shape=obs_shape, z_dim=z_dim)


        # # reduce model size

        # torch.save({
        #     'hi_model_state_dict': agent_hi.state_dict(),
        #     'lo_model_state_dict': agent_lo.state_dict()
        #         }, f"{agent_name}_model.pt")




        lstm_state_lo = (
            torch.zeros(agent_lo.lstm.num_layers, 1, agent_lo.lstm.hidden_size),
            torch.zeros(agent_lo.lstm.num_layers, 1, agent_lo.lstm.hidden_size),
        )   
        lstm_state_hi = (
            torch.zeros(agent_hi.lstm.num_layers, 1, agent_hi.lstm.hidden_size),
            torch.zeros(agent_hi.lstm.num_layers, 1, agent_hi.lstm.hidden_size),
        )
        next_done = torch.zeros(1)

        agent_obs = torch.randn(1, 26, 8, 5)

        with torch.no_grad():
            current_lstm_state_lo = (lstm_state_lo[0].clone(), lstm_state_lo[1].clone())
            current_lstm_state_hi = (lstm_state_hi[0].clone(), lstm_state_hi[1].clone())

            z, _, ent, ___, lstm_state_hi, ____ = agent_hi.get_z_and_value(agent_obs, next_done, lstm_state_hi)

            agent_actions, _, __, ___, _____, ______, lstm_state_lo = agent_lo.get_action_and_value(agent_obs, z, next_done, current_lstm_state_lo)
            
            print("Predicted action:", agent_actions)
