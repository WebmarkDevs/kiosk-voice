### Documentation for Dockerized Environment with `.env.local`

---

### **Setup Steps**

1. **Create `.env.local`**:
   ```
   ENV=dev
   ```

2. **Project Structure**:
   ```
   .
   ├── Dockerfile.agent
   ├── Dockerfile.main
   ├── docker-compose.yml
   ├── requirements.txt
   ├── agent.py
   ├── main.py
   ├── .env.local
   ```

3. **Run**:
   ```bash
   docker-compose up --build
   ```

---

### **Stop Services**:
```bash
docker-compose down
```