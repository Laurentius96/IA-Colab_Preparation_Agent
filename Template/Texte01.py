---

```markdown
## 🎓 **Aula sobre: A Função `print()` e F-Strings**

<br>

### 🧭 Sumário da Aula

| # | Sub-tópico                      | Tempo Estimado | Complexidade |
|---|---------------------------------|----------------|--------------|
| 1 | Ficha de Revisão Rápida         | ~1 min         | ⭐           |
| 2 | Mergulho Profundo               | ~15 min        | ⭐⭐⭐⭐       |
| 3 | Profundezas e Conexões          | ~3 min         | ⭐⭐         |
| 4 | Ação e Verificação              | ~5 min         | ⭐⭐         |
| 5 | Mergulhos Adicionais            | Opcional       | ⭐⭐⭐⭐       |

<br>

---
<br>
```

---

```markdown
### 1. 🧠 Ficha de Revisão Rápida | (O Essencial)

<br>

> A função `print()` exibe valores no console e aceita parâmetros como `sep`, `end`, `file` e `flush`.  
> *F-strings* são literais de string prefixados com `f` que permitem interpolar expressões dentro de chaves `{}` e usar especificadores de formatação (ex: `:.2f`).

<br>

### 2. 🔬 Mergulho Profundo | (Os Detalhes)

<br>

#### **🎯 O Conceito Central**  
- `print(*args, sep=' ', end='\n', file=sys.stdout, flush=False)` envia texto formatado para *stdout*.  
- *F-strings* avaliam expressões em tempo de execução, criando a string resultante antes do envio a `print()`.

<br>

#### **🔗 Analogia de Data Science**  
Imagine gerar relatórios em que você mescla texto estático com valores calculados (ex: média de vendas). `print()` é a impressora que sai do pipeline, e *f-strings* são os moldes que unem dados e texto de forma clara e eficiente.

<br>

### **💻 Exemplos de Mercado (Abrangentes)**
```

---

```markdown
#### **Nível Simples: Uso básico de `print()`**
```

---

▶️ **Código para Executar (Célula):**

```python
print("A", "B", "C", sep="-", end="!\n")
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Imprime “A-B-C!” no console, usando `-` como separador e `!`+quebra de linha ao final.  
*   **Cenário de Mercado:** Útil para moldar logs ou apresentações de dados sequenciais.  
*   **Boas Práticas:** Use parâmetros para clareza em saídas complexas.
```

---

```markdown
#### **Nível Intermediário: F-Strings Básicas**
```

---

▶️ **Código para Executar (Célula):**

```python
nome = "Lorenzo"
idade = 28
print(f"Olá, {nome}. Você tem {idade} anos.")
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Interpola as variáveis `nome` e `idade` na string.  
*   **Cenário de Mercado:** Base para gerar templates de relatórios com dados dinâmicos.  
*   **Boas Práticas:** Evite concatenar strings com `+`, prefira *f-strings* pela legibilidade.
```

---

```markdown
#### **Nível Avançado: Formatação Avançada com F-Strings**
```

---

▶️ **Código para Executar (Célula):**

```python
pi = 3.1415926535
print(f"Valor de π: {pi:.2f}")
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Formata `pi` com duas casas decimais.  
*   **Cenário de Mercado:** Essencial em dashboards financeiros e científicos.  
*   **Boas Práticas:** Use especificadores (`:.2f`, `:>8`, etc.) para alinhar e padronizar saídas.
```

---

```markdown
#### **Nível DEUS (1/3): Impressão em Arquivo e Flush**
```

---

▶️ **Código para Executar (Célula):**

```python
with open("log.txt", "a") as log:
    print("Registro de evento", file=log, flush=True)
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Escreve no arquivo “log.txt” e força gravação imediata.  
*   **Cenário de Mercado:** Importante em sistemas de logging e auditoria de processos.  
*   **Boas Práticas:** Use `flush=True` para evitar perda de dados em encerramentos abruptos.
```

---

```markdown
#### **Nível DEUS (2/3): Depuração com F-Strings (`=`)**
```

---

▶️ **Código para Executar (Célula):**

```python
x = 10
y = 20
print(f"{x=} e {y=}")
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Imprime `x=10 e y=20`, mostrando nomes e valores.  
*   **Cenário de Mercado:** Agiliza debug sem escrever múltiplos `print()`.  
*   **Boas Práticas:** Use em desenvolvimento, remova em produção para não vazar dados.
```

---

```markdown
#### **Nível DEUS (3/3): F-Strings Multilinha e Expressões**
```

---

▶️ **Código para Executar (Célula):**

```python
user = {"nome":"Lorenzo", "idade":28}
print(f"""
Usuário:
 Nome : {user['nome']}
 Idade: {user['idade']}
Data : {__import__('datetime').date.today()}
""")
```

📖 **Texto para Leitura (Markdown):**

```markdown
*   **O que o código faz:** Usa f-string multilinha, inclui expressões e chamadas de função.  
*   **Cenário de Mercado:** Gera relatórios complexos e templates de e-mail automatizados.  
*   **Boas Práticas:** Cuidado com indentação e performance de expressões pesadas.
```

````
---
```markdown
### 3. 🕸️ Profundezas e Conexões

<br>
`print()` é amplamente substituído por frameworks de *logging* em produção para níveis de severidade e formatação avançada. *F-strings* são parte do *PEP 498* e superam `.format()` e `%` em performance e legibilidade. Conectar saída formatada a relatórios HTML/Markdown facilita dashboards automatizados.
<br>

---
<br>
````

---

```markdown
### 4. 🚀 Ação e Verificação

<br>
#### **🤔 Desafio Prático**
1. Use `print()` para exibir `"Bem-vindo ao sistema"` sem quebra de linha ao final.  
2. Dada a lista `itens = ["caneta","caderno","borracha"]`, imprima-os separados por `"; "`.  
3. Crie `produto="Caneta"`, `preco=2.5` e use *f-string* para exibir `Produto: Caneta — R$ 2.50`.  
4. Defina `pi=3.14159`, `e=2.71828` e exiba ambos com 3 casas decimais em uma única f-string.  
5. Explique por que `print(a, b)` e `print(f"{a} {b}")` podem produzir resultados diferentes.

<br>
#### **❓ Pergunta de Verificação**
Quando usar *f-strings* em vez de concatenação (`+`) ou operador `%`? Quais vantagens de performance e segurança elas oferecem?
<br>

---
<br>
```

5 🌊 Mergulhos Adicionais Opcionais

* Uso de `logging` vs `print()`
* Método `.format()` e *Template Strings*
* Performance: *f-strings* vs `.format()` vs `%`
* Outras Sugestões
* Voltar ao Menu Opções

