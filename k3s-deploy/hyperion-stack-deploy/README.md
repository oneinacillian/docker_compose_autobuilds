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
2. **Create a project in Harbor** named `hyperion` and make it public (or set up credentials for private).
3. **Tag and push your image** to Harbor:

   ```sh
   docker tag <your-image> harbor-test.oiac.io/hyperion/hyperion:latest
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