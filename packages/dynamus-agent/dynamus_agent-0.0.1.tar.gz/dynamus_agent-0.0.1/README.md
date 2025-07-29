# ⚙️ dynamus-agent

**Agente base del ecosistema Dynamus**

`dynamus-agent` es la piedra angular para construir agentes inteligentes y modulares dentro del ecosistema Dynamus. Diseñado con principios de extensibilidad, descubrimiento dinámico y sinergia entre componentes.

---

## 🧩 Artefacto

```text
📦 dynamus-agent
├── 🔧 agent_base.py      # Clase base común para todos los agentes
├── 🧠 capabilities.py    # Capacidades definidas para agentes
├── 🛰️ discovery.py       # Mecanismo de descubrimiento de agentes
├── 📓 registry.py        # Registro dinámico de agentes
├── 🚨 exceptions.py      # Excepciones específicas del framework
└── 📁 __init__.py
```

---

## 🚀 Instalación

```bash
pip install dynamus-agent
```

O bien instalá todo el ecosistema:

```bash
pip install dynamus
```

---

## 🔍 Funcionalidades principales

- Creación de agentes inteligentes con interfaz común.
- Registro y descubrimiento en tiempo de ejecución.
- Integración con `dynamus-core` y protocolos MCP/CLI.
- Sistema de capacidades y especialización de agentes.

---

## 🧠 Ejemplo básico

```python
from dynamus_agent import DynamusAgent

class MyAgent(DynamusAgent):
    def run(self):
        print("Hola desde MyAgent!")

agent = MyAgent(name="test-agent")
agent.run()
```

---

## 📄 Licencia

MIT License — Federico Monfasani · [fmonfasani@gmail.com](mailto:fmonfasani@gmail.com)

---

## 🤝 Contribuciones

¡Pull requests bienvenidos! Este paquete forma parte del ecosistema [Dynamus](https://pypi.org/project/dynamus/).
