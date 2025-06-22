#!/usr/bin/env python3
import pika
import sys
import time

def test_loadbalancer():
    print("Testing HAProxy Load Balancer for RabbitMQ...")
    print("=" * 50)
    
    try:
        # Connect to RabbitMQ through HAProxy load balancer
        print("Connecting to RabbitMQ via HAProxy (localhost:5675)...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost', 
                port=5675, 
                credentials=pika.PlainCredentials('rabbitmquser', 'rabbitmqpass'),
                virtual_host='hyperion'
            )
        )
        
        print("✓ Successfully connected to RabbitMQ through HAProxy!")
        
        channel = connection.channel()
        
        # Declare a test queue
        queue_name = 'test_lb_queue'
        print(f"\nDeclaring queue: {queue_name}")
        result = channel.queue_declare(queue=queue_name, durable=True)
        print(f"✓ Queue declared successfully")
        
        # Publish a test message
        message = f"Test message from HAProxy load balancer at {time.strftime('%H:%M:%S')}"
        print(f"\nPublishing message: {message}")
        channel.basic_publish(
            exchange='', 
            routing_key=queue_name, 
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
        print("✓ Message published successfully")
        
        # Consume the message
        print(f"\nConsuming message from queue: {queue_name}")
        method_frame, header_frame, body = channel.basic_get(queue_name)
        
        if method_frame:
            print(f"✓ Message received: {body.decode()}")
            channel.basic_ack(method_frame.delivery_tag)
            print("✓ Message acknowledged")
        else:
            print("✗ No message received")
        
        # Clean up
        print(f"\nCleaning up test queue: {queue_name}")
        channel.queue_delete(queue=queue_name)
        print("✓ Test queue deleted")
        
        connection.close()
        print("\n✓ Connection closed successfully")
        print("\n🎉 HAProxy Load Balancer Test: SUCCESS!")
        
    except pika.exceptions.AMQPConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure HAProxy is running and listening on port 5675")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_loadbalancer() 