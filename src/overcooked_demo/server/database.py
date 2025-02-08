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
        """Inserts a new record and its transition data into the database."""
        try:
            transition = data["trajectory"]

            # Insert into trajectories table
            insert_trajectory_query = """
            INSERT INTO trajectories (
                state, joint_action, reward, time_left, score, time_elapsed, 
                cur_gameloop, layout, layout_name, trial_id, player_0_id, 
                player_1_id, player_0_is_human, player_1_is_human, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """

            self.cursor.execute(
                insert_trajectory_query,
                (
                    transition["state"],
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

            trajectory_id = self.cursor.fetchone()[0]

            # Insert into records table
            insert_record_query = """
            INSERT INTO records (uid, timestamp, trajectory_id) VALUES (%s, %s, %s);
            """
            self.cursor.execute(insert_record_query, (data["uid"], data['timestamp'], trajectory_id))

            # Commit the transaction
            self.conn.commit()
            print(f"Inserted record with UID {data['uid']} and Trajectory ID {trajectory_id} at {data['timestamp']}")

        except psycopg2.Error as e:
            self.conn.rollback()
            print("Database update failed:", e)

    def close(self):
        """Closes the database connection."""
        self.cursor.close()
        self.conn.close()
