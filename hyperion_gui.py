import os
from generate_hyperion_compose import *
import subprocess

class HyperionCLI:
    def __init__(self):
        self.configs = {
            'Number of Nodes': '1',
            'Elasticsearch Version': '8.13.2',
            'Elastic Min Memory': '1g',
            'Elastic Max Memory': '2g',
            'Kibana Version': '8.13.2',
            'RabbitMQ User': 'rabbitmquser',
            'RabbitMQ Password': 'rabbitmqpass',
            'Hyperion Environment': 'testnet',
            'Hyperion Version': 'v3.3.10-1'
        }

    def show_menu(self):
        while True:
            print("\nHyperion Docker Manager")
            print("----------------------")
            print("1. Show Current Configuration")
            print("2. Update Configuration")
            print("3. Generate Docker Compose")
            print("4. Start Services")
            print("5. Stop Services")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == '1':
                self.show_config()
            elif choice == '2':
                self.update_config()
            elif choice == '3':
                self.generate_compose()
            elif choice == '4':
                self.docker_compose_up()
            elif choice == '5':
                self.docker_compose_down()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")

    def show_config(self):
        print("\nCurrent Configuration:")
        for key, value in self.configs.items():
            print(f"{key}: {value}")

    def update_config(self):
        print("\nEnter new values (press Enter to keep current value):")
        for key, current_value in self.configs.items():
            new_value = input(f"{key} [{current_value}]: ")
            if new_value:
                self.configs[key] = new_value

    def generate_compose(self):
        try:
            # Update environment variables
            os.environ["AMOUNT_OF_NODE_INSTANCES"] = self.configs['Number of Nodes']
            os.environ["ELASTICSEARCH_VERSION"] = self.configs['Elasticsearch Version']
            os.environ["ELASTIC_MIN_MEM"] = self.configs['Elastic Min Memory']
            os.environ["ELASTIC_MAX_MEM"] = self.configs['Elastic Max Memory']
            os.environ["KIBANA_VERSION"] = self.configs['Kibana Version']
            os.environ["RABBITMQ_DEFAULT_USER"] = self.configs['RabbitMQ User']
            os.environ["RABBITMQ_DEFAULT_PASS"] = self.configs['RabbitMQ Password']
            os.environ["HYPERION_ENVIRONMENT"] = self.configs['Hyperion Environment']
            os.environ["HYPERION_VERSION"] = self.configs['Hyperion Version']
            
            # Generate the compose file
            final_compose = base_compose + services + volumes_and_networks.format(volumes=volumes)
            with open("docker-compose-generated-hyperion.yml", "w") as f:
                f.write(final_compose)
                
            print("Docker Compose file generated successfully!")
        except Exception as e:
            print(f"Error: Failed to generate Docker Compose file: {str(e)}")

    def docker_compose_up(self):
        try:
            subprocess.run(["docker-compose", "-f", "docker-compose-generated-hyperion.yml", "up", "-d"], check=True)
            print("Services started successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error starting services: {str(e)}")

    def docker_compose_down(self):
        try:
            subprocess.run(["docker-compose", "-f", "docker-compose-generated-hyperion.yml", "down"], check=True)
            print("Services stopped successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping services: {str(e)}")

if __name__ == "__main__":
    app = HyperionCLI()
    app.show_menu() 