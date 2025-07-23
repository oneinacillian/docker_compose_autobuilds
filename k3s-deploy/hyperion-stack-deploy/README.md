# 🚀 Hyperion Stack Deployment on Kubernetes

Deploy a full Hyperion stack—including Elasticsearch, Redis, RabbitMQ, Kibana, and Hyperion—on your Kubernetes cluster using ArgoCD and Harbor.

---

## Prerequisites

- **Kubernetes cluster** (k3s, k3d, or any K8s provider)
- **kubectl** installed and configured
- **ArgoCD** installed and running
- **Harbor** registry (public or private)
- **Personal Access Token (PAT)** for your Git repository

---

## 1. Add Your Git Repository to ArgoCD

1. **Create a Personal Access Token** with access to your repository.
2. **Authenticate ArgoCD to your repository:**

   ```sh
   kubectl exec -n argocd argocd-application-controller-0 -- \
     sh -c 'argocd login cd.argoproj.io --core && \
     argocd repo add https://github.com/oneinacillian/docker_compose_autobuilds \
     --username <your-username> --password <your-github-pat>'
   ```

---

## 2. Build and Push Hyperion Images

1. **Build your Hyperion images** using the Dockerfile in `hyperion-stack-deploy/hyperion-app/build`.
   ```sh
    Sending build context to Docker daemon  3.072kB
    Step 1/10 : FROM node:20
    20: Pulling from library/node
    Digest: sha256:dc2a18571982a2d76e61e5fa823c65013f6ee2c58a24d764db4e757c688b01b0
    Status: Image is up to date for node:20
    ---> d05db19b2fc9
    Step 2/10 : RUN mkdir -p /app
    ---> Using cache
    ---> 60ceaf8c8dd3
    Step 3/10 : WORKDIR /app
    ---> Using cache
    ---> eee2c8c7b9bf
    Step 4/10 : RUN npm install -g pm2
    ---> Using cache
    ---> 3a2905423f13
    Step 5/10 : RUN apt-get update && apt-get install -y git vim
    ---> Using cache
    ---> 3e6f8a77cf2b
    Step 6/10 : RUN git clone -b v3.3.10-1 https://github.com/eosrio/hyperion-history-api.git /app
    ---> Using cache
    ---> 38d7bd404191
    Step 7/10 : COPY ./entrypoint.sh .
    ---> Using cache
    ---> 4a98a72687d0
    Step 8/10 : RUN npm install
    ---> Using cache
    ---> 60b386675425
    Step 9/10 : RUN chmod +x ./entrypoint.sh
    ---> Using cache
    ---> 5ad0fe93b55f
    Step 10/10 : ENTRYPOINT ["./entrypoint.sh"]
    ---> Using cache
    ---> 8692ecf6d04d
    Successfully built 8692ecf6d04d
    Successfully tagged test:test
   ```
2. **Create a project in Harbor** named `hyperion` and make it public (or set up credentials for private).
3. **Tag and push your image** to Harbor:

   ```sh
   docker login harbor-test.oiac.io
   docker tag test:test harbor-test.oiac.io/hyperion/hyperion:latest
   docker push harbor-test.oiac.io/hyperion/hyperion:latest
   ```

   > **Note:** The Hyperion deployment in Kubernetes references this image.

---

## 3. Deploy the Stack with ArgoCD

Apply each application manifest to ArgoCD using `kubectl`:

```sh
kubectl apply -f hyperion-stack-deploy/elasticsearch-app/application.yaml
kubectl apply -f hyperion-stack-deploy/redis-app/application.yaml
kubectl apply -f hyperion-stack-deploy/rabbitmq-app/application.yaml
kubectl apply -f hyperion-stack-deploy/kibana-app/application.yaml
kubectl apply -f hyperion-stack-deploy/hyperion-app/application.yaml
```

---

## 4. Access Your Stack

- **Kibana:** http://<your-kibana-domain>
- **Hyperion API:** http://<your-hyperion-domain>:7000
- **Harbor UI:** https://harbor-test.oiac.io

> Replace `<your-kibana-domain>` and `<your-hyperion-domain>` with your actual ingress hostnames.

---

## 5. Need Help?

- Check the [ArgoCD UI](http://<your-argocd-domain>) for sync and health status.
- Review pod logs with `kubectl logs`.
- Visit [Hyperion Docs](https://github.com/eosrio/Hyperion-History-API) for more info.

---

**Happy indexing! 🚀**