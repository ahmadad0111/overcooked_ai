import json
import psycopg2


class Database:
    def __init__(self, config_file="db.json"):
        # Load database credentials
        with open(config_file, "r") as file:
            self.config = json.load(file)

        # Establish database connection
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()

    def update(self, data):
        """Inserts new records and their transition data into the database."""
        try:
            transition_list = data["trajectory"]
            commit_hash = data["hash_key"]

            # Prepare insert query for the trajectories table
            insert_trajectory_query = """
            INSERT INTO trajectories (
                hash_key, state, joint_action, reward, time_left, score, time_elapsed, 
                cur_gameloop, layout, layout_name, trial_id, player_0_id, 
                player_1_id, player_0_is_human, player_1_is_human, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """

            # Iterate over the list of trajectory dictionaries and insert them
            for transition in transition_list:
                self.cursor.execute(
                    insert_trajectory_query,
                    (
                        commit_hash,  # Insert hash_key first
                        transition['state'],
                        transition["joint_action"],
                        transition["reward"],
                        transition["time_left"],
                        transition["score"],
                        transition["time_elapsed"],
                        transition["cur_gameloop"],
                        transition["layout"],
                        transition["layout_name"],
                        transition["trial_id"],
                        transition["player_0_id"],
                        transition["player_1_id"],
                        transition["player_0_is_human"],
                        transition["player_1_is_human"],
                        transition["timestamp"]
                    ),
                )

            # Insert into records table
            insert_record_query = """
            INSERT INTO records (uid, timestamp, hash_key) VALUES (%s, %s, %s);
            """
            # here i need subject id
            self.cursor.execute(insert_record_query, (data["uid"], data['timestamp'], commit_hash))
            print('Record inserted successfully.')
            print( data['timestamp'])            

            # Commit the transaction
            self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()
            print("Database update failed:", e)

    def close(self):
        """Closes the database connection."""
        self.cursor.close()
        self.conn.close()
