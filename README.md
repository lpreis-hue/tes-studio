# TeS Studio

Aplicativo desktop para simulação de equilíbrio termodinâmico com minimização
de energia de Gibbs e maximização de entropia. Esta evolução mantém o núcleo
numérico do TeS-IPOPT e organiza a interface, os recursos e o empacotamento.

A interface técnica escura organiza cada módulo em três áreas: dados de
entrada, parâmetros e acompanhamento da execução. O total de cenários é
mostrado antes da simulação e o andamento apresenta percentual e estimativa
de tempo restante.

## Executar em desenvolvimento

O caminho recomendado, especialmente no Windows, é usar Conda porque o
`cyipopt` depende das bibliotecas nativas do IPOPT:

```powershell
conda env create -f environment.yml
conda activate tes-studio
python scripts/check_project.py
python scripts/smoke_test.py
python main.py
```

## Gerar o aplicativo portátil no Windows

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

O resultado é `dist/TeS Studio/TeS Studio.exe`. Distribua a pasta inteira;
ela contém as DLLs e os recursos necessários. Consulte
[`docs/BUILD_WINDOWS.md`](docs/BUILD_WINDOWS.md) para diagnóstico e detalhes.

## Gerar na nuvem em um repositório privado

O projeto inclui `.github/workflows/build-windows.yml`. Após enviar os arquivos
para um repositório privado, execute **Build Windows portable** na aba Actions.
O GitHub gerará `TeS-Studio-Windows-x64.zip` como artefato privado. O passo a
passo está em
[`docs/GITHUB_PRIVATE_REPOSITORY.md`](docs/GITHUB_PRIVATE_REPOSITORY.md).

## Organização

- `main.py`: janela principal e navegação.
- `app/screens/`: telas e fluxo da interface.
- `app/ui/`: tema visual compartilhado.
- `app/gibbs.py` e `app/entropy.py`: modelos numéricos preservados.
- `app/auxiliar_func/`: cálculo e leitura de dados preservados.
- `packaging/`, `tes.spec` e `scripts/`: build e verificações.
- `.github/workflows/`: build Windows na nuvem e publicação do ZIP privado.

O arquivo `numerical_core.sha256.json` protege os módulos de cálculo contra
alterações acidentais durante a evolução visual. Veja também
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

Nas simulações com vários valores de temperatura e pressão, o resultado do
ponto anterior é usado somente como estimativa inicial para o IPOPT no ponto
vizinho. Cada ponto continua sendo resolvido com seus próprios balanços,
limites e tolerâncias.

## Documentação científica original

O TeS — Thermodynamic Equilibrium Simulation — é um software de código aberto
voltado a estudos de equilíbrio termodinâmico e sistemas reacionais. A base
científica original é documentada abaixo.

### 1. Minimização de Energia de Gibbs (*minG*):

Este módulo permite que o usuário simule o reator isotérmico utilizando a abordagem de minimização de energia de Gibbs. Referências sobre o desenvolvimento matemático podem ser obtidas em trabalhos anteriores reportados por Mitoura and Mariano (2024).

Como já dito, o objetivo é minimizar a energia de Gibbs e esta será escrita na forma de programação não-linear como apresenta a equação abaixo:

$$min G = \sum_{i=1}^{NC} \sum_{j=1}^{NF} n_i^j \mu_i^j$$

O passo seguinte é o cálculo da energia de Gibbs. A equação abaixo apresentação a realção entra entalpia e capacidade calorífica.

$$\frac{\partial \bar{H}_i^g}{\partial T} = Cp_i^g \text{  para } i=1,\ldots,NC$$

Tendo conhecimento da realação da entalpia com a temperatura, o passo seguinte é o cálculo do potencial químico. A equação abaixo apresenta a correlação para o cálculo dos potenciais químicos.

$$\frac{\partial}{\partial T} \left( \frac{\mu_i^g}{RT} \right) = -\frac{\bar{H}_i^g}{RT^2} \quad \text{para } i=1,\ldots,NC$$

Temos então o cálculo do potencial químico do componente *i*:

$$
\mu_i^0 = \frac {T}{T^0} \Delta G_f^{298.15 K} - T \int_{T_0}^{T} \frac {\Delta H_f^{298.15 K} + \int_{T_0}^{T} (CPA + CPB \cdot T + CPC \cdot T^2 + \frac{CPD}{T^2}) \, dT}{T^2} \, dT
$$

Tendo conhecimento dos potenciais químicos, podemos definir a função objetivo:

$$\min G = \sum_{i=1}^{NC} n_i^g \mu_i^g $$

Onde:

$$\mu _i^g = \mu _i^0 + R.T.(ln(\phi_i)+ln(P)+ln(y_i)) $$

Para os calculos dos coeficientes de fugacidade, teremos duas possibilidades:

1. Gás ideal: 

$$\phi = 1 $$

2. Gás não ideal:

Para gases não ideais, o cálculo dos coeficientes de fugacidade é feito com base em equações cúbicas de estado, com suporte às seguintes opções:

- Peng-Robinson (PR)
- Soave-Redlich-Kwong (SRK)
- Redlich-Kwong (RK)
- Virial (Truncada no segundo termo)

Os detalhes serão apresentados na seção 1.1 deste texto.

Conhecemos a função objetivo (minG), agora precisamos definir as restrições para direcionar a busca pela solução.

O espaço de possíveis soluções deve ser restrito a duas condições:

1. Não negatividade de mols:

$$ n_i^j \geq 0 $$

2. Conservação do número de átomos:

$$
\sum_{i=1}^{NC} a_{mi} \left(\sum_{j=1}^{NF} n_{i}^{j}\right) = \sum_{i=1}^{NC} a_{mi} n_{i}^{0}
$$


A rotina descrita aqui pode ser encontrada no seguinte camiho:

```
└── 📁app
    └── gibbs.py
```


Referências:

Mitoura, Julles.; Mariano, A.P. Gasification of Lignocellulosic Waste in Supercritical Water: Study of Thermodynamic Equilibrium as a Nonlinear Programming Problem. Eng 2024, 5, 1096-1111. https://doi.org/10.3390/eng5020060

---





#### 1.1 Cálculo dos Coeficientes de Fugacidade ($\phi_i$):

##### **Equações Cúbicas de Estado (PR, SRK, RK)**

Para cada componente:

* Temperatura crítica: ($T_{c,i}$)
* Pressão crítica: ($P_{c,i}$)
* Fator acêntrico: ($\omega_i$)

Com base na equação de estado escolhida, os seguintes parâmetros são definidos:

* Constantes específicas da EOS: ($\Omega_a$), ($\Omega_b$)
* Parâmetro de atração ajustado à temperatura:

$$
m_i =
\begin{cases}
0.37464 + 1.54226 \cdot \omega_i - 0.26992 \cdot \omega_i^2 & \text{(Peng-Robinson)} \\
0.480 + 1.574 \cdot \omega_i - 0.176 \cdot \omega_i^2 & \text{(SRK)} \\
0 & \text{(RK)}
\end{cases}
$$

$$
\alpha_i =
\begin{cases}
\left(1 + m_i(1 - \sqrt{T/T_{c,i}})\right)^2 & \text{(PR ou SRK)} \\
\frac{1}{\sqrt{T/T_{c,i}}} & \text{(RK)}
\end{cases}
$$

$$
a_i = \Omega_a \cdot \left( \frac{R^2 T_{c,i}^2}{P_{c,i}} \right) \cdot \alpha_i
\quad ; \quad
b_i = \Omega_b \cdot \left( \frac{R T_{c,i}}{P_{c,i}} \right)
$$

* Parâmetro de interação binária: ($k_{ij}$)

$$a_{ij} = (1 - k_{ij}) \cdot \sqrt{a_i \cdot a_j}$$

$$
a_{\text{mix}} = \sum_i \sum_j y_i y_j a_{ij}
\quad ; \quad
b_{\text{mix}} = \sum_i y_i b_i
$$

$$
A = \frac{a_{\text{mix}} P}{R^2 T^2}
\quad ; \quad
B = \frac{b_{\text{mix}} P}{R T}
$$

A equação cúbica é escrita como:

$$Z^3 + c_2 Z^2 + c_1 Z + c_0 = 0$$

Os coeficientes dependem da EOS:

* **Peng-Robinson (PR):**

    $$Z^3 + (B - 1)Z^2 + (A - 2B - 3B^2)Z + (-AB + B^2 + B^3) = 0$$

* **SRK / RK:**

    $$Z^3 - Z^2 + (A - B - B^2)Z - AB = 0$$

Seleciona-se a maior raiz real positiva ($Z$) que representa a fase gás.

Para cada componente ($i$):

$$\ln \phi_i = \frac{b_i}{b_{\text{mix}}}(Z - 1) - \ln(Z - B) - \frac{A}{B} \cdot \left( \frac{2 \sum_j y_j a_{ij}}{a_{\text{mix}}} - \frac{b_i}{b_{\text{mix}}} \right) \cdot f(Z, B)$$

Com:

* Para PR:

    $$f(Z, B) = \frac{1}{2\sqrt{2}} \cdot \ln\left( \frac{Z + (1 + \sqrt{2})B}{Z + (1 - \sqrt{2})B} \right)$$

* Para SRK/RK:

    $$f(Z, B) = \ln\left(1 + \frac{B}{Z} \right)$$

##### **Equação de Virial (2º Termo)**

A equação de Virial truncada no segundo termo relaciona o fator de compressibilidade com a pressão:

$$Z = 1 + \frac{B_{mix} P}{RT}$$

O segundo coeficiente de Virial para a mistura ($B_{mix}$) é calculado usando a seguinte regra de mistura:

$$B_{mix} = \sum_{i=1}^{NC} \sum_{j=1}^{NC} y_i y_j B_{ij}$$

Onde $B_{ii}$ é o coeficiente do componente puro e $B_{ij}$ é o coeficiente cruzado para o par i-j. Esses coeficientes são dependentes da temperatura e geralmente são obtidos por correlações empíricas baseadas em propriedades críticas.

O logaritmo do coeficiente de fugacidade para cada componente *i* na mistura é dado por:

$$\ln \phi_i = \left[ 2 \sum_{j=1}^{NC} y_j B_{ij} - B_{mix} \right] \frac{P}{RT}$$

Finalmente, para qualquer um dos modelos:
$$\phi_i = \exp(\ln \phi_i)$$

Para componentes sólidos, assume-se ($\phi_i = 1.0$).

A rotina descrita aqui pode ser encontrada no seguinte camiho:

```
└── 📁app
    └── 📁auxiliar_func
        └── eos.py
```

### 2. Maximização de Entropia (*maxS*):

Este módulo permite simular reatores adiabáticos com volume fixo utilizando a abordagem de maximização da entropia total do sistema. Essa técnica é amplamente adotada na literatura para determinar o estado de equilíbrio em sistemas isolados. A formulação é apresentada a seguir com base no desenvolvimento implementado.

A função objetivo consiste em maximizar a entropia total, o que pode ser reescrito como um problema de minimização do valor negativo da entropia total:

$$
\max S = \sum_{i=1}^{NC} n_i^g \cdot \bar{S}_i^g
$$

ou equivalentemente,

$$
\min (-S) = - \sum_{i=1}^{NC} n_i^g \cdot \bar{S}_i^g
$$

Onde $n_i^g$ é o número de mols do componente i na fase gasosa e $\bar{S}_i^g$ é a entropia molar desse componente.

O cálculo da entropia molar dos gases considera:

	•	Contribuições entrópicas padrão a 298.15 K;

	•	Variações com a temperatura via capacidades caloríficas;

	•	Termos relacionados à composição e pressão do sistema.

A expressão geral adotada para a entropia molar é:

$$
\bar{S}i^g = \left(\frac{\Delta H{f,i}^{298.15} - \Delta G_{f,i}^{298.15}}{T_0}\right) - R \ln(P) - R \ln(y_i) + \int_{T_0}^{T} \frac{C_{p,i}(T)}{T} , dT
$$

Com:

$T_0$ = 298.15 \, K: temperatura padrão de referência;

$R$: constante dos gases;

$y_i$: fração molar do componente i;

$C_{p,i}(T)$: capacidade calorífica em função da temperatura.

A capacidade calorífica é modelada como:

$$
C_{p,i}(T) = CPA_i + CPB_i \cdot T + CPC_i \cdot T^2 + \frac{CPD_i}{T^2}
$$

Portanto, a integral da entropia em função de T é:

$$
\int_{T_0}^{T} \frac{C_{p,i}(T)}{T} , dT = CPA_i \cdot \ln\left(\frac{T}{T_0}\right) + CPB_i \cdot (T - T_0) + \frac{CPC_i}{2} \cdot (T^2 - T_0^2) - \frac{CPD_i}{2} \cdot \left(\frac{1}{T^2} - \frac{1}{T_0^2}\right)
$$

Restrições

O problema de maximização de entropia está sujeito a duas classes principais de restrições:
	1.	Conservação de átomos:

$$
\sum_{i=1}^{NC} a_{mi} \cdot n_i^g = \sum_{i=1}^{NC} a_{mi} \cdot n_i^0
$$

Onde:

$a_{mi}$: número de átomos do elemento m no componente i;

$n_i^0$: número inicial de mols do componente i.


A entalpia total antes e depois da reação deve permanecer constante:

$$
\sum_{i=1}^{NC} n_i^g \cdot \bar{H}i^g(T) = \sum{i=1}^{NC} n_i^0 \cdot \bar{H}_i^g(T_0)
$$

A entalpia molar $\bar{H}_i^g$ é calculada com base na temperatura:

$$
\bar{H}i^g(T) = \Delta H{f,i}^{298.15} + \int_{T_0}^{T} C_{p,i}(T) , dT
$$

A rotina descrita aqui pode ser encontrada no seguinte camiho:

```
└── 📁app
    └── entropy.py
```



### Solver IPOPT:

Em todos os módulos de simulação deste projeto — minimização de energia de Gibbs, maximização de entropia e ajuste de parâmetros de ELV — o núcleo do problema reside em encontrar a solução ótima para um sistema descrito por equações complexas e não-lineares. Para essa tarefa, foi escolhido o solver **IPOPT**.

**IPOPT (Interior Point Optimizer)** é um pacote de software de código aberto de alta performance, projetado especificamente para resolver problemas de **otimização não-linear (NLP - Nonlinear Programming)** em larga escala.

A escolha do IPOPT para o TeS v3 não foi acidental e se baseia em vários motivos técnicos fundamentais:

1.  **Natureza do Problema Termodinâmico**: Os problemas de equilíbrio químico e de fases são inerentemente não-lineares. As funções objetivo (como a energia de Gibbs ou a entropia) e as restrições (como a igualdade de fugacidade) dependem de logaritmos de frações molares ($ ln(y_i) $), equações de estado cúbicas e outras relações complexas, que não podem ser resolvidas com métodos de programação linear. IPOPT é especializado para esta classe de problemas.

2.  **Tratamento Robusto de Restrições**: O IPOPT utiliza um **método de pontos interiores (ou método de barreira)**, que é extremamente eficaz no tratamento de problemas com restrições de igualdade (ex: balanço atômico, balanço de energia, igualdade de fugacidade) e de desigualdade (ex: não-negatividade do número de mols, $n_i \ge 0$). Ele aborda a solução ótima a partir do interior da região viável, o que o torna robusto para os tipos de restrições encontrados em termodinâmica.

3.  **Convergência e Estabilidade**: Modelos termodinâmicos podem ser numericamente sensíveis. O IPOPT é reconhecido na comunidade acadêmica e industrial por sua excelente performance e capacidade de convergir para uma solução ótima (ou localmente ótima) de forma estável e eficiente, mesmo para funções complexas e mal condicionadas.

4.  **Integração com Pyomo**: O código para o ajuste de ELV utiliza o framework de modelagem **Pyomo**. O IPOPT é um dos solvers padrão e mais bem integrados ao Pyomo, permitindo que a formulação matemática do problema seja traduzida de forma direta e confiável para um formato que o solver entende. Essa sinergia simplifica o desenvolvimento e a manutenção do código.

5.  **Filosofia de Código Aberto**: Assim como o TeS, o IPOPT é um projeto de código aberto (parte da iniciativa COIN-OR). Sua utilização garante que o software seja totalmente livre, acessível e transparente, alinhando-se com os objetivos do projeto de fomentar o estudo e a pesquisa em termodinâmica.

Em resumo, o IPOPT foi escolhido por ser uma ferramenta poderosa, validada, de código aberto e tecnicamente adequada para a classe de problemas de otimização não-linear encontrados na simulação de equilíbrio termodinâmico, garantindo resultados precisos e confiáveis para os usuários do **TeS**.

Dentro deste projeto, o solver deve ser apresentado no seguinte caminho:

```
└── 📁app
    └── 📁solver
```

Para download do solver, utilize este endereço.

https://github.com/coin-or/Ipopt/releases

---


## Processo de build

O processo atual usa o ambiente Conda e o script descrito no início deste
documento. Consulte [`docs/BUILD_WINDOWS.md`](docs/BUILD_WINDOWS.md). O arquivo
`tes.spec` inclui os recursos da interface, a planilha termodinâmica e as
bibliotecas nativas necessárias ao `cyipopt`.
