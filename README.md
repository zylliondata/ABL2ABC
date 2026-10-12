# ABL2ABC: From "Atomic Business Loops" to "Atomic Business Capabilities" — An Industrial Software Compiler

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![CI](https://github.com/zylliondata/ABL2ABC/actions/workflows/ci.yml/badge.svg)](https://github.com/zylliondata/ABL2ABC/actions/workflows/ci.yml)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/zylliondata/ABL2ABC)
[![Gitee](https://img.shields.io/badge/Gitee-C71D23?logo=gitee&logoColor=white)](https://gitee.com/zylliondata/AMT2ABC)

**English** | [简体中文](./README.zh-CN.md)

---

**ABL2ABC** is an open-source ecosystem for compiling industrial software capabilities. It takes Atomic Business Loop (**ABL**) as business input, and automatically compiles industrial mechanisms, expressed as Atomic Mechanism Triplets (**AMTs**), into reusable Atomic Business Capabilities (**ABCs**), enabling automated transformation from business goals to executable industrial applications.

> What industrial software lacks is not AI, but a Compiler.
> — ABL2ABC core thesis

## Why ABL2ABC?

Traditional industrial software development has long been trapped in a "project-based, siloed, costly-to-change" dilemma. Capabilities are hard to reuse across production lines and processes, and every change requires extensive manual code modification. Drawing on Huawei's Tau (τ) Law and the historical lessons of RISC + Compiler, ABL2ABC shifts complexity from low-level code to the instance-configuration layer, letting the system automatically understand business goals and compile recommended capability combinations.

## Core Concepts

| Concept | Full Name | Description |
|---------|-----------|-------------|
| **AMT** | Atomic Mechanism Triplet | The smallest irreducible industrial causal unit, e.g. "load ↑ → vibration ↑" |
| **SECP** | Structure, Event, Configuration, Process | The four-dimensional grammar of industrial software, providing unified structural labels for AMT |
| **ABC** | Atomic Business Capability | A minimum software capability unit that can be independently deployed and reused across scenarios |
| **Compiler** | ABL2ABC Compiler | The system that automatically extracts AMT Clusters from business goals (GS), packages them as ABCs, and orchestrates them into Apps/Agents |

## Architecture Overview

```
Working Domain → Mechanism → AMT → AMT Graph
                                           ↓
               GS (Goal) → AMT Cluster → ABC
                                           ↓
             App/Agent → Scenario → OAO Loop
```

- **Human-defined parts**: Working Domain, Mechanism, AMT, AMT Graph
- **Compiler-automated parts**: GS → AMT Cluster → ABC → App/Agent

## Quick Start

### Prerequisites

- Basic understanding of industrial mechanisms
- Familiarity with YAML/JSON configuration

### Install the Compiler Prototype (MVP)

```bash
# From GitHub
git clone https://github.com/zylliondata/ABL2ABC.git

# From Gitee (faster in mainland China)
git clone https://gitee.com/zylliondata/AMT2ABC.git

cd ABL2ABC
# Detailed installation steps: docs/installation.md (coming soon)
```

### Minimal Example

Input goal: "Reduce porosity rate" (die-casting line)

Compiler outputs a recommended ABC combination (JSON example):

```json
{
  "goal": "Reduce porosity rate",
  "recommended_abc": ["Mold-Temperature Control ABC", "Shot-Speed Optimization ABC", "Vacuum Management ABC"]
}
```

For a full tutorial, see `docs/getting-started.md` (coming soon).

## Open-Source Roadmap

| Phase | Timeline | Goal |
|-------|----------|------|
| 1. Hands-on Prototype | This year Q3 | Open-source Compiler MVP + die-casting line example |
| 2. Community Contributions | This year Q4+ | Open contribution channels for AMT/SECP patterns |
| 3. ABC Registry | Next year | An ABC capability marketplace, similar to Docker Hub |
| 4. Standardization | Three years out | Domestic group standards → international standards |

## Contributing

We welcome contributions in all forms, including but not limited to:

- Submitting new AMT patterns or SECP fingerprints
- Packaging and sharing ABC modules
- Improving the Compiler's matching algorithm
- Improving documentation and tutorials

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed workflows.

## Code of Conduct

This project follows the Contributor Covenant Code of Conduct. Please read the [full text](CODE_OF_CONDUCT.md).

## Security

To report a security vulnerability, please follow the process in [SECURITY.md](SECURITY.md).

## License

[Apache 2.0 License](LICENSE) © ABL2ABC Contributors

## Contact

[![GitHub Issues](https://img.shields.io/badge/GitHub%20Issues-181717?logo=github&logoColor=white)](https://github.com/zylliondata/ABL2ABC/issues)
[![Gitee Issues](https://img.shields.io/badge/Gitee%20Issues-C71D23?logo=gitee&logoColor=white)](https://gitee.com/zylliondata/AMT2ABC/issues)
[![GitHub Discussions](https://img.shields.io/badge/GitHub%20Discussions-181717?logo=github&logoColor=white)](https://github.com/zylliondata/ABL2ABC/discussions)
[![Email](https://img.shields.io/badge/Email-info%40zylliondata.com-blue?logo=gmail&logoColor=white)](mailto:info@zylliondata.com)
