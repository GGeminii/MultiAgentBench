---
license: other
task_categories:
- token-classification
- reinforcement-learning
- robotics
- feature-extraction
- text-generation
language:
- en
tags:
- manufacturing
- AI
- NER
- industrial
- Artificial intelligence
- Named entity recognition
- Manufacturing systems
- Dataset
- Code automation
- Large language models
pretty_name: AutoFactory
size_categories:
- 10K<n<100K
---

# 🏭 AutoFactory: Extracting Key Components for Code Generation in Manufacturing Systems

![Hugging Face](https://huggingface.co/front/assets/huggingface_logo-noborder.svg)

## 🔍 What is AutoFactory?
- AutoFactory is a public dataset of requirement specifications describing manufacturing systems (Factory I/O scenarios). It is built for Named Entity Recognition (NER) so AI models can extract key components from natural language and assist in PLC control code generation.
> **Relation to Factory I/O:** Factory I/O provides 3D manufacturing systems; **AutoFactory provides the textual specifications** that describe such systems.

## 🌟 Why use AutoFactory?
- Extracts **Actuator**, **Pre-actuator**, **Sensor**, **Effector**, **Other** from text (BIO tags)
- Supports text-to-code research for industrial control
- CoNLL-like 5-column format: token, POS tag, POS index, NER label, NER index
- Delivered in CSV and XLSX for direct use

## 📅 Version Information
- **Version:** 2.0 (Second Release)
- **Future Updates:** Each new version will include more samples, additional manufacturing components, and extended annotations.

## 🗂️ Dataset structure & splits
- **Total**: 2,358 specifications • 17,134 sentences • 279,830 tokens  
- **Labels (token counts)**: Actuators 19,851 · Pre-actuators 5,913 · Sensors 25,695 · Effectors 26,640 · Others 201,731
 
**Split (80/10/10):**
- **Train**: 1,886 specs · 13,686 sentences · 223,003 tokens  
- **Validation**: 236 specs · 1,728 sentences · 28,759 tokens  
- **Test**: 236 specs · 1,720 sentences · 28,068 tokens

## 📝 Example (BIO)
“The system includes a **conveyor belt** driven by an **electric motor**.”  
- conveyor → `B-EFFECTOR`, belt → `I-EFFECTOR`  
- electric → `B-ACTUATOR`, motor → `I-ACTUATOR`

## 🧪 Quality & augmentation
- Human-written baselines + LLM reformulations (ChatGPT Pro, Claude Pro, Mistral Pro)  
- **Semantic similarity** (cosine) between originals and rewrites: avg 0.9275, median 0.9389  
- **Inter-annotator agreement** on reviewed subset: Cohen’s κ = 0.856

## 📊 Baselines (NER)
Fine-tuned transformers on AutoFactory: DistilBERT-Base reached **F1 = 0.9505** (precision 0.9476, recall 0.9534) under a consistent setup (3 epochs, lr=5e-5, batch=16).

## 🔖 POS Tag Mapping  
The dataset includes POS tagging to help models understand syntactic structures in requirement specifications. Each POS tag is mapped to a numeric index for model training:

```python
pos = {',': 0, '.': 1, ':': 2, 'CC': 3, 'CD': 4, 'DT': 5, 'IN': 6, 'JJ': 7, 'MD':{',': 0, '.': 1, ':': 2, 'CC': 3, 'CD': 4, 'DT': 5, 'EX': 6, 'IN': 7, 'JJ': 8, 'MD': 9, 'NN': 10, 'NNP': 11, 'NNS': 12, 'POS': 13, 'PRP': 14, 'PRP$': 15, 'RB': 16, 'RBR': 17, 'RP': 18, 'TO': 19, 'VB': 20, 'VBD': 21, 'VBG': 22, 'VBN': 23, 'VBP': 24, 'VBZ': 25, 'WDT': 26, 'WRB': 27}
```

## 🏷️ NER Tag Mapping
The NER labels identify key components in manufacturing automation. Each label is mapped to a numeric index:
```python
ner = {'O': 0, 'B-ACTUATOR': 1, 'I-ACTUATOR': 2, 'B-PREACTUATOR': 3, 'I-PREACTUATOR': 4, 'B-SENSOR': 5, 'I-SENSOR': 6, 'B-EFFECTOR': 7, 'I-EFFECTOR': 8}
```

## 📋 Tokenized and Annotated Format
| **Token** | **POS** | **POS Index** | **NER Label** | **NER Index** |
| :-------: | :-----: | :-----------: | :-----------: | :-----------: |
|    The    |    DT   |       5       |       O       |       0       |
|   system  |    NN   |       10      |       O       |       0       |
|  consists |   VBZ   |       25      |       O       |       0       |
|     of    |    IN   |       7       |       O       |       0       |
|     a     |    DT   |       5       |       O       |       0       |
|  conveyor |    NN   |       10      |   B-EFFECTOR  |       7       |
|    belt   |    NN   |       10      |   I-EFFECTOR  |       8       |
|   driven  |   VBN   |       23      |       O       |       0       |
|     by    |    IN   |       7       |       O       |       0       |
|     an    |    DT   |       5       |       O       |       0       |
|  electric |    JJ   |       8       |   B-ACTUATOR  |       1       |
|   motor   |    NN   |       10      |   I-ACTUATOR  |       2       |

## 🛠️ Usage
You can load the dataset using Hugging Face’s datasets library:
```python
from datasets import load_dataset
dataset = load_dataset("boudribila/AutoFactory")
```

## 🔬 Applications
AI-driven PLC programming (text → control logic)
NER training for industrial language
Industrial AI research on requirement interpretation

## 📖 Citation
If you use AutoFactory in your research, please cite:  
Data article (Available at): <https://www.sciencedirect.com/science/article/pii/S2352340925006626>

<!--
This is a comment
-->

## 📬 Contact
- For any questions, improvements, or collaborations, feel free to reach out at [a.boudribila.ced@uca.ac.ma](mailto:a.boudribila.ced@uca.ac.ma)