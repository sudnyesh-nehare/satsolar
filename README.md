---

## Deployment

### Backend — Render
- Platform: [render.com](https://render.com) (free tier)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- Auto-deploys on every push to `main` branch

### Frontend — Cloudflare Pages
- Platform: Cloudflare Pages (free)
- Build directory: `frontend`
- Custom domain: `satsolar.symbianslab.com`

---

## Known Limitations

- Free tier on Render sleeps after 15 minutes of inactivity — first request after sleep takes 30–60 seconds
- Model is retrained per location on every cold start (cached in memory during runtime)
- Savings estimate uses average Indian electricity rate of Rs. 8/kWh — may vary by region
- Prediction accuracy depends on NASA POWER data availability for the selected location

---

## About

**Sudnyesh Nehare**  
Cybersecurity Associate · Ex-Intern at DRDO (Blockchain & Network Security)  
B.E. Computer Science, Sant Gadge Baba Amravati University (2026)  
Nagpur, Maharashtra, India

**SymbiansLab**  
A startup that solves problems others don't even realize exist.  
Building smart, innovative tools that make technology simpler and more effective.  
Founded July 2025 · Nagpur, Maharashtra

- Website: [symbianslab.com](https://www.symbianslab.com)
- YouTube: [@SymbiansLab](https://www.youtube.com/@SymbiansLab)
- LinkedIn: [SymbiansLab](https://www.linkedin.com/company/symbianslab/)
- Email: symbianslab@gmail.com

---

## License

MIT License — free to use, modify, and distribute with attribution.
EOF