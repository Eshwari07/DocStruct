---
source_file: upload.pdf
source_format: pdf
total_pages: 14
extracted_at: 2026-03-20T15:42:05.322641Z
extraction_path: fast
---

# 1 · ﻿Identification of a 9-gene autophagy-related signature for predicting prognosis and immune exhaustion features in breast cancer

ORIGINAL ARTICLE
used for risk stratification but often fail to fully capture 
the intricate biological complexity of the disease (Benson 
2003; Cserni et al. 2018). Consequently, a substantial pro­
portion of patients with similar clinical features experience 
vastly different prognoses, with many suffering from unex­
pected recurrence, distant metastasis, and the development 
of multi-drug resistance (Tran et al. 2018; Afzal and Vah­
dat 2024). This persistent clinical dilemma underscores an

## 1.1 · ﻿Abstract

ORIGINAL ARTICLE
used for risk stratification but often fail to fully capture 
the intricate biological complexity of the disease (Benson 
2003; Cserni et al. 2018). Consequently, a substantial pro­
portion of patients with similar clinical features experience 
vastly different prognoses, with many suffering from unex­
pected recurrence, distant metastasis, and the development 
of multi-drug resistance (Tran et al. 2018; Afzal and Vah­
dat 2024). This persistent clinical dilemma underscores an 
urgent need to identify novel, robust molecular biomarkers 
that can transcend traditional staging systems to optimize 
risk assessment and guide personalized precision medicine 
(Meehan et al. 2020; Afzal and Vahdat 2024).
In the context of tumorigenesis, autophagy functions as a 
complex “double-edged sword,” a duality well-documented 
in breast cancer research(Gu et al. 2016; Chavez-Dominguez 
et al. 2020; Klionsky et al. 2021). On one hand, autophagy 
acts as a tumor suppressor in early neoplastic transforma­
tion. For instance, the monoallelic deletion of the essential 
autophagy gene BECN1 (Beclin 1) is observed in 40–75% of 
breast cancers, where its loss promotes genomic instability 
and accelerates mammary tumorigenesis (Liang et al. 1999, 
p. 1; Yu et al. 2024b). However, in established tumors, the 
role of autophagy often shifts towards promoting survival 
and therapeutic resistance. Cancer cells hijack this mecha­
nism to mitigate metabolic stress and evade cytotoxicity. 
Specific examples include the observation that protective 
Introduction
Breast cancer (BRCA) has surpassed lung cancer as the 
most frequently diagnosed malignancy worldwide, posing 
a tremendous challenge to global public health(Sung et al. 
2021; Fumagalli and Barberis 2021). According to recent 
global cancer statistics, BRCA remains the leading cause 
of cancer-related mortality among women, with incidence 
rates continuing to rise in both developed and developing 
regions(Baliu-Piqué et al. 2020). Currently, the standard 
of care involves a multimodal approach comprising sur­
gical resection, chemotherapy, radiotherapy, endocrine 
therapy, and targeted biological agents (e.g., anti-HER2 
therapies) (Shenkier 2004; Grunfeld 2005; Greenlee et al. 
2017). Despite significant advancements in these thera­
peutic strategies, the clinical outcomes of BRCA patients 
remain highly heterogeneous. Traditional clinicopathologi­
cal indicators, such as TNM staging, histological grade, and 
molecular subtyping (ER, PR, HER2 status), are widely 
	
 Mengsha Zou
zoumengsha88@163.com
Department of Breast and Thyroid Surgery, The Affiliated 
Lihuili Hospital of Ningbo University, Ningbo 315040, 
Zhejiang, P. R. China
Abstract
To address the prognostic limitations in breast cancer (BRCA), we integrated transcriptomic profiles from The Cancer 
Genome Atlas (TCGA) and Gene Expression Omnibus (GEO) to construct a novel 9-gene autophagy-related signature 
via Least Absolute Shrinkage and Selection Operator (LASSO) Cox regression. The model demonstrated robust predictive 
accuracy for overall survival in the training cohort (HR = 2.28, P < 0.001) and maintained stability in external validation 
(AUC = 0.740). Mechanistically, the risk score was significantly associated with selective autophagy pathways and an 
immune-exhausted microenvironment characterized by T-cell dysfunction. Furthermore, drug sensitivity profiling identi­
fied a positive correlation between the risk gene MTDH and sensitivity to Vincristine and Gemcitabine. This study presents 
a reliable risk-stratification tool that bridges autophagic mechanisms with personalized chemotherapy guidance.
Keywords  Breast cancer · Autophagy · Prognostic signature · Immune exhaustion · Drug sensitivity · Bioinformatics
Received: 6 January 2026 / Accepted: 17 February 2026
© The Author(s) 2026
Identification of a 9-gene autophagy-related signature for predicting 
prognosis and immune exhaustion features in breast cancer
Jianan Zhang1 · Yijun Wang1 · Mengsha Zou1

## 1.2 · ﻿Introduction

ORIGINAL ARTICLE
used for risk stratification but often fail to fully capture 
the intricate biological complexity of the disease (Benson 
2003; Cserni et al. 2018). Consequently, a substantial pro­
portion of patients with similar clinical features experience 
vastly different prognoses, with many suffering from unex­
pected recurrence, distant metastasis, and the development 
of multi-drug resistance (Tran et al. 2018; Afzal and Vah­
dat 2024). This persistent clinical dilemma underscores an 
urgent need to identify novel, robust molecular biomarkers 
that can transcend traditional staging systems to optimize 
risk assessment and guide personalized precision medicine 
(Meehan et al. 2020; Afzal and Vahdat 2024).
In the context of tumorigenesis, autophagy functions as a 
complex “double-edged sword,” a duality well-documented 
in breast cancer research(Gu et al. 2016; Chavez-Dominguez 
et al. 2020; Klionsky et al. 2021). On one hand, autophagy 
acts as a tumor suppressor in early neoplastic transforma­
tion. For instance, the monoallelic deletion of the essential 
autophagy gene BECN1 (Beclin 1) is observed in 40–75% of 
breast cancers, where its loss promotes genomic instability 
and accelerates mammary tumorigenesis (Liang et al. 1999, 
p. 1; Yu et al. 2024b). However, in established tumors, the 
role of autophagy often shifts towards promoting survival 
and therapeutic resistance. Cancer cells hijack this mecha­
nism to mitigate metabolic stress and evade cytotoxicity. 
Specific examples include the observation that protective 
Introduction
Breast cancer (BRCA) has surpassed lung cancer as the 
most frequently diagnosed malignancy worldwide, posing 
a tremendous challenge to global public health(Sung et al. 
2021; Fumagalli and Barberis 2021). According to recent 
global cancer statistics, BRCA remains the leading cause 
of cancer-related mortality among women, with incidence 
rates continuing to rise in both developed and developing 
regions(Baliu-Piqué et al. 2020). Currently, the standard 
of care involves a multimodal approach comprising sur­
gical resection, chemotherapy, radiotherapy, endocrine 
therapy, and targeted biological agents (e.g., anti-HER2 
therapies) (Shenkier 2004; Grunfeld 2005; Greenlee et al. 
2017). Despite significant advancements in these thera­
peutic strategies, the clinical outcomes of BRCA patients 
remain highly heterogeneous. Traditional clinicopathologi­
cal indicators, such as TNM staging, histological grade, and 
molecular subtyping (ER, PR, HER2 status), are widely 
	
 Mengsha Zou
zoumengsha88@163.com
Department of Breast and Thyroid Surgery, The Affiliated 
Lihuili Hospital of Ningbo University, Ningbo 315040, 
Zhejiang, P. R. China
Abstract
To address the prognostic limitations in breast cancer (BRCA), we integrated transcriptomic profiles from The Cancer 
Genome Atlas (TCGA) and Gene Expression Omnibus (GEO) to construct a novel 9-gene autophagy-related signature 
via Least Absolute Shrinkage and Selection Operator (LASSO) Cox regression. The model demonstrated robust predictive 
accuracy for overall survival in the training cohort (HR = 2.28, P < 0.001) and maintained stability in external validation 
(AUC = 0.740). Mechanistically, the risk score was significantly associated with selective autophagy pathways and an 
immune-exhausted microenvironment characterized by T-cell dysfunction. Furthermore, drug sensitivity profiling identi­
fied a positive correlation between the risk gene MTDH and sensitivity to Vincristine and Gemcitabine. This study presents 
a reliable risk-stratification tool that bridges autophagic mechanisms with personalized chemotherapy guidance.
Keywords  Breast cancer · Autophagy · Prognostic signature · Immune exhaustion · Drug sensitivity · Bioinformatics
Received: 6 January 2026 / Accepted: 17 February 2026
© The Author(s) 2026
Identification of a 9-gene autophagy-related signature for predicting 
prognosis and immune exhaustion features in breast cancer
Jianan Zhang1 · Yijun Wang1 · Mengsha Zou1

## 1.3 · ﻿Materials and methods

### 1.3.1 · ﻿Data collection and preprocessing

autophagy mediates acquired resistance to Tamoxifen in ER-
positive breast cancer by preventing apoptosis (Samaddar et 
al. 2008), and facilitates survival in HER2-positive tumors 
treated with Trastuzumab (Triulzi et al. 2018). Similarly, in 
triple-negative breast cancer (TNBC), elevated autophagic 
flux has been linked to reduced sensitivity to taxane-based 
chemotherapies like Paclitaxel, where autophagy inhibi­
tors have been shown to restore drug efficacy (Luo et al. 
2016). Given this pivotal role, ARGs hold immense promise 
as potential biomarkers, yet their systemic integration into 
prognostic models remains to be fully explored(Jin et al. 
2022; Yu et al. 2024a).
Despite the revolutionary success of immune checkpoint 
inhibitors (ICIs) in melanoma and lung cancer, their effi­
cacy in breast cancer remains limited. Most breast tumors 
exhibit an immunologically ‘cold’ phenotype characterized 
by low T-cell infiltration and intrinsic resistance to PD-1/
PD-L1 blockade (Emens 2018). Therefore, deciphering the 
molecular mechanisms that drive immune exclusion and 
exhaustion is a top priority. Recent research has highlighted 
a dynamic crosstalk between autophagy, the tumor micro­
environment (TME), and drug sensitivity. Dysregulated 
autophagy can reshape the immune landscape, often lead­
ing to an immunosuppressive microenvironment. A semi­
nal study demonstrated that pancreatic cancer cells utilize 
selective autophagy mediated by the receptor NBR1 to 
degrade MHC-I molecules, thereby impairing antigen pre­
sentation and allowing tumors to evade CD8 + T cell kill­
ing (Yamamoto et al. 2020). In the context of breast cancer, 
autophagy has also been implicated in regulating the sta­
bility of the immune checkpoint protein PD-L1, directly 
influencing the efficacy of immunotherapy (Clark et al. 
2017). Furthermore, metabolic stress in the TME can induce 
maladaptive autophagy in infiltrating T cells, contributing 
to a state of “exhaustion” where T cells lose their effec­
tor functions and upregulate inhibitory receptors (Wherry 
2011). Despite these isolated findings, few studies have 
successfully constructed a unified model that links ARG 
expression patterns simultaneously to immune exhaustion 
status and chemotherapeutic sensitivity (Xia et al. 2021; 
Jin et al. 2022). Therefore, identifying a robust signature 
that can bridge these biological mechanisms with clinical 
precision medicine is essential for advancing breast can­
cer management(Deng et al. 2021). Although autophagy is 
known to modulate immune responses, systematic studies 
linking autophagy-related gene signatures directly to the 
‘immune-exhausted’ phenotype in breast cancer are lacking. 
Current prognostic models rarely integrate these two critical 
biological processes to guide immunotherapy.
In the present study, we systematically analyzed the 
expression profiles of ARGs in BRCA using large-scale 
transcriptomic data from The Cancer Genome Atlas 
(TCGA) and Gene Expression Omnibus (GEO) databases. 
We constructed a robust 9-gene autophagy-related prognos­
tic signature via LASSO Cox regression analysis. Beyond 
prognostic prediction, we extensively investigated the asso­
ciation between the signature and the immune landscape, 
revealing a potential mechanism of immune exhaustion in 
high-risk patients. Furthermore, we screened for potential 
sensitive drugs targeting high-risk patients, providing new 
insights for precision medicine and therapeutic decision-
making in breast cancer.
Materials and methods
Data collection and preprocessing
Publicly available RNA-sequencing (RNA-seq) data 
(HTSeq-FPKM) and corresponding clinical information of 
Breast Invasive Carcinoma (BRCA) were obtained from 
The Cancer Genome Atlas (TCGA) database (​h​t​t​p​s​:​/​/​p​o​r​t​a​l​.​
g​d​c​.​c​a​n​c​e​r​.​g​o​v​/) (The Cancer Genome Atlas Research ​N​e​t​w​
o​r​k et al. 2013), serving as the training cohort. For external 
validation, an independent microarray dataset [GSE20685] 
was retrieved from the Gene Expression Omnibus (GEO) 
database (​h​t​t​p​s​:​/​/​w​w​w​.​n​c​b​i​.​n​l​m​.​n​i​h​.​g​o​v​/​g​e​o​/) (Barrett et al. 
2012). The raw data were normalized and log2-transformed 
to ensure data comparability. Additionally, a comprehensive 
list of 232 ARGs was downloaded from the Human Autoph­
agy Database (HADb, http://www.autophagy.lu/) (Moussay 
et al. 2011).
Identification of differentially expressed autophagy-
related genes (DE-ARGs)
Differential expression analysis between breast cancer tis­
sues and normal tissues was performed using the limma 
package inR software (version 4.4.2) (Ritchie et al. 2015). 
The selection criteria were set as a False Discovery Rate 
(FDR) < 0.05 and |log2 Fold Change| > 1. The identified 
DEGs were then intersected with the ARG list from HADb 
to obtain the DE-ARGs.
Screening of prognostic candidates
To screen for genes with significant prognostic value, the 
Kaplan-Meier Plotter database ​(​h​t​t​p​s​:​/​/​k​m​p​l​o​t​.​c​o​m​/​a​n​a​l​y​s​i​
s​/​) was utilized (Győrffy 2021). The identified DE-ARGs 
were entered into the system, and the “auto select best cut­
off” option was applied to stratify patients. Genes with a 
Log-rank P < 0.05 in the Overall Survival (OS) analysis were 
considered potential prognostic candidates and selected for 
further modeling.

### 1.3.2 · ﻿Identification of differentially expressed autophagy-related genes (DE-ARGs)

autophagy mediates acquired resistance to Tamoxifen in ER-
positive breast cancer by preventing apoptosis (Samaddar et 
al. 2008), and facilitates survival in HER2-positive tumors 
treated with Trastuzumab (Triulzi et al. 2018). Similarly, in 
triple-negative breast cancer (TNBC), elevated autophagic 
flux has been linked to reduced sensitivity to taxane-based 
chemotherapies like Paclitaxel, where autophagy inhibi­
tors have been shown to restore drug efficacy (Luo et al. 
2016). Given this pivotal role, ARGs hold immense promise 
as potential biomarkers, yet their systemic integration into 
prognostic models remains to be fully explored(Jin et al. 
2022; Yu et al. 2024a).
Despite the revolutionary success of immune checkpoint 
inhibitors (ICIs) in melanoma and lung cancer, their effi­
cacy in breast cancer remains limited. Most breast tumors 
exhibit an immunologically ‘cold’ phenotype characterized 
by low T-cell infiltration and intrinsic resistance to PD-1/
PD-L1 blockade (Emens 2018). Therefore, deciphering the 
molecular mechanisms that drive immune exclusion and 
exhaustion is a top priority. Recent research has highlighted 
a dynamic crosstalk between autophagy, the tumor micro­
environment (TME), and drug sensitivity. Dysregulated 
autophagy can reshape the immune landscape, often lead­
ing to an immunosuppressive microenvironment. A semi­
nal study demonstrated that pancreatic cancer cells utilize 
selective autophagy mediated by the receptor NBR1 to 
degrade MHC-I molecules, thereby impairing antigen pre­
sentation and allowing tumors to evade CD8 + T cell kill­
ing (Yamamoto et al. 2020). In the context of breast cancer, 
autophagy has also been implicated in regulating the sta­
bility of the immune checkpoint protein PD-L1, directly 
influencing the efficacy of immunotherapy (Clark et al. 
2017). Furthermore, metabolic stress in the TME can induce 
maladaptive autophagy in infiltrating T cells, contributing 
to a state of “exhaustion” where T cells lose their effec­
tor functions and upregulate inhibitory receptors (Wherry 
2011). Despite these isolated findings, few studies have 
successfully constructed a unified model that links ARG 
expression patterns simultaneously to immune exhaustion 
status and chemotherapeutic sensitivity (Xia et al. 2021; 
Jin et al. 2022). Therefore, identifying a robust signature 
that can bridge these biological mechanisms with clinical 
precision medicine is essential for advancing breast can­
cer management(Deng et al. 2021). Although autophagy is 
known to modulate immune responses, systematic studies 
linking autophagy-related gene signatures directly to the 
‘immune-exhausted’ phenotype in breast cancer are lacking. 
Current prognostic models rarely integrate these two critical 
biological processes to guide immunotherapy.
In the present study, we systematically analyzed the 
expression profiles of ARGs in BRCA using large-scale 
transcriptomic data from The Cancer Genome Atlas 
(TCGA) and Gene Expression Omnibus (GEO) databases. 
We constructed a robust 9-gene autophagy-related prognos­
tic signature via LASSO Cox regression analysis. Beyond 
prognostic prediction, we extensively investigated the asso­
ciation between the signature and the immune landscape, 
revealing a potential mechanism of immune exhaustion in 
high-risk patients. Furthermore, we screened for potential 
sensitive drugs targeting high-risk patients, providing new 
insights for precision medicine and therapeutic decision-
making in breast cancer.
Materials and methods
Data collection and preprocessing
Publicly available RNA-sequencing (RNA-seq) data 
(HTSeq-FPKM) and corresponding clinical information of 
Breast Invasive Carcinoma (BRCA) were obtained from 
The Cancer Genome Atlas (TCGA) database (​h​t​t​p​s​:​/​/​p​o​r​t​a​l​.​
g​d​c​.​c​a​n​c​e​r​.​g​o​v​/) (The Cancer Genome Atlas Research ​N​e​t​w​
o​r​k et al. 2013), serving as the training cohort. For external 
validation, an independent microarray dataset [GSE20685] 
was retrieved from the Gene Expression Omnibus (GEO) 
database (​h​t​t​p​s​:​/​/​w​w​w​.​n​c​b​i​.​n​l​m​.​n​i​h​.​g​o​v​/​g​e​o​/) (Barrett et al. 
2012). The raw data were normalized and log2-transformed 
to ensure data comparability. Additionally, a comprehensive 
list of 232 ARGs was downloaded from the Human Autoph­
agy Database (HADb, http://www.autophagy.lu/) (Moussay 
et al. 2011).
Identification of differentially expressed autophagy-
related genes (DE-ARGs)
Differential expression analysis between breast cancer tis­
sues and normal tissues was performed using the limma 
package inR software (version 4.4.2) (Ritchie et al. 2015). 
The selection criteria were set as a False Discovery Rate 
(FDR) < 0.05 and |log2 Fold Change| > 1. The identified 
DEGs were then intersected with the ARG list from HADb 
to obtain the DE-ARGs.
Screening of prognostic candidates
To screen for genes with significant prognostic value, the 
Kaplan-Meier Plotter database ​(​h​t​t​p​s​:​/​/​k​m​p​l​o​t​.​c​o​m​/​a​n​a​l​y​s​i​
s​/​) was utilized (Győrffy 2021). The identified DE-ARGs 
were entered into the system, and the “auto select best cut­
off” option was applied to stratify patients. Genes with a 
Log-rank P < 0.05 in the Overall Survival (OS) analysis were 
considered potential prognostic candidates and selected for 
further modeling.

### 1.3.3 · ﻿Screening of prognostic candidates

autophagy mediates acquired resistance to Tamoxifen in ER-
positive breast cancer by preventing apoptosis (Samaddar et 
al. 2008), and facilitates survival in HER2-positive tumors 
treated with Trastuzumab (Triulzi et al. 2018). Similarly, in 
triple-negative breast cancer (TNBC), elevated autophagic 
flux has been linked to reduced sensitivity to taxane-based 
chemotherapies like Paclitaxel, where autophagy inhibi­
tors have been shown to restore drug efficacy (Luo et al. 
2016). Given this pivotal role, ARGs hold immense promise 
as potential biomarkers, yet their systemic integration into 
prognostic models remains to be fully explored(Jin et al. 
2022; Yu et al. 2024a).
Despite the revolutionary success of immune checkpoint 
inhibitors (ICIs) in melanoma and lung cancer, their effi­
cacy in breast cancer remains limited. Most breast tumors 
exhibit an immunologically ‘cold’ phenotype characterized 
by low T-cell infiltration and intrinsic resistance to PD-1/
PD-L1 blockade (Emens 2018). Therefore, deciphering the 
molecular mechanisms that drive immune exclusion and 
exhaustion is a top priority. Recent research has highlighted 
a dynamic crosstalk between autophagy, the tumor micro­
environment (TME), and drug sensitivity. Dysregulated 
autophagy can reshape the immune landscape, often lead­
ing to an immunosuppressive microenvironment. A semi­
nal study demonstrated that pancreatic cancer cells utilize 
selective autophagy mediated by the receptor NBR1 to 
degrade MHC-I molecules, thereby impairing antigen pre­
sentation and allowing tumors to evade CD8 + T cell kill­
ing (Yamamoto et al. 2020). In the context of breast cancer, 
autophagy has also been implicated in regulating the sta­
bility of the immune checkpoint protein PD-L1, directly 
influencing the efficacy of immunotherapy (Clark et al. 
2017). Furthermore, metabolic stress in the TME can induce 
maladaptive autophagy in infiltrating T cells, contributing 
to a state of “exhaustion” where T cells lose their effec­
tor functions and upregulate inhibitory receptors (Wherry 
2011). Despite these isolated findings, few studies have 
successfully constructed a unified model that links ARG 
expression patterns simultaneously to immune exhaustion 
status and chemotherapeutic sensitivity (Xia et al. 2021; 
Jin et al. 2022). Therefore, identifying a robust signature 
that can bridge these biological mechanisms with clinical 
precision medicine is essential for advancing breast can­
cer management(Deng et al. 2021). Although autophagy is 
known to modulate immune responses, systematic studies 
linking autophagy-related gene signatures directly to the 
‘immune-exhausted’ phenotype in breast cancer are lacking. 
Current prognostic models rarely integrate these two critical 
biological processes to guide immunotherapy.
In the present study, we systematically analyzed the 
expression profiles of ARGs in BRCA using large-scale 
transcriptomic data from The Cancer Genome Atlas 
(TCGA) and Gene Expression Omnibus (GEO) databases. 
We constructed a robust 9-gene autophagy-related prognos­
tic signature via LASSO Cox regression analysis. Beyond 
prognostic prediction, we extensively investigated the asso­
ciation between the signature and the immune landscape, 
revealing a potential mechanism of immune exhaustion in 
high-risk patients. Furthermore, we screened for potential 
sensitive drugs targeting high-risk patients, providing new 
insights for precision medicine and therapeutic decision-
making in breast cancer.
Materials and methods
Data collection and preprocessing
Publicly available RNA-sequencing (RNA-seq) data 
(HTSeq-FPKM) and corresponding clinical information of 
Breast Invasive Carcinoma (BRCA) were obtained from 
The Cancer Genome Atlas (TCGA) database (​h​t​t​p​s​:​/​/​p​o​r​t​a​l​.​
g​d​c​.​c​a​n​c​e​r​.​g​o​v​/) (The Cancer Genome Atlas Research ​N​e​t​w​
o​r​k et al. 2013), serving as the training cohort. For external 
validation, an independent microarray dataset [GSE20685] 
was retrieved from the Gene Expression Omnibus (GEO) 
database (​h​t​t​p​s​:​/​/​w​w​w​.​n​c​b​i​.​n​l​m​.​n​i​h​.​g​o​v​/​g​e​o​/) (Barrett et al. 
2012). The raw data were normalized and log2-transformed 
to ensure data comparability. Additionally, a comprehensive 
list of 232 ARGs was downloaded from the Human Autoph­
agy Database (HADb, http://www.autophagy.lu/) (Moussay 
et al. 2011).
Identification of differentially expressed autophagy-
related genes (DE-ARGs)
Differential expression analysis between breast cancer tis­
sues and normal tissues was performed using the limma 
package inR software (version 4.4.2) (Ritchie et al. 2015). 
The selection criteria were set as a False Discovery Rate 
(FDR) < 0.05 and |log2 Fold Change| > 1. The identified 
DEGs were then intersected with the ARG list from HADb 
to obtain the DE-ARGs.
Screening of prognostic candidates
To screen for genes with significant prognostic value, the 
Kaplan-Meier Plotter database ​(​h​t​t​p​s​:​/​/​k​m​p​l​o​t​.​c​o​m​/​a​n​a​l​y​s​i​
s​/​) was utilized (Győrffy 2021). The identified DE-ARGs 
were entered into the system, and the “auto select best cut­
off” option was applied to stratify patients. Genes with a 
Log-rank P < 0.05 in the Overall Survival (OS) analysis were 
considered potential prognostic candidates and selected for 
further modeling.

### 1.3.4 · ﻿Construction and validation of the prognostic signature

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

### 1.3.5 · ﻿Functional enrichment and ppi network analysis

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

### 1.3.6 · ﻿Assessment of independent prognostic factors

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

### 1.3.7 · ﻿Immune infiltration and drug sensitivity analysis

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

### 1.3.8 · ﻿Protein level validation

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

### 1.3.9 · ﻿Statistical analysis

Construction and validation of the prognostic 
signature
To construct a robust prognostic model and minimize the 
risk of overfitting, Least Absolute Shrinkage and Selection 
Operator (LASSO) Cox regression analysis was performed 
using the glmnet package in R(Friedman et al. 2010). We 
employed a 10-fold cross-validation strategy to optimize 
the penalty parameter (λ). Specifically, the training dataset 
was randomly partitioned into 10 non-overlapping subsets. 
In each iteration, the model was trained on nine subsets 
and validated on the remaining one to calculate the partial 
likelihood deviance. This process was repeated 10 times to 
ensure the stability of the results(Lin and Zelterman 2002). 
The optimal λ value was ultimately determined based on the 
minimum partial likelihood deviance criteria λ min, yield­
ing the most parsimonious model with the best predictive 
performance.
The risk score for each patient was calculated using the 
following formula:
Risk Score =
n
∑
i = 1
(Coefi × Expi)
Where Coef i,represents the regression coefficient derived 
from the multivariate Cox analysis, and Exp i represents the 
normalized expression value of gene i. Patients were cate­
gorized into high- and low-risk groups based on the median 
risk score. Kaplan-Meier (K-M) survival curves and Time-
dependent Receiver Operating Characteristic (ROC) curves 
were generated using the survival and timeROC packages 
(Blanche et al. 2013) to evaluate the predictive performance 
in both the TCGA training cohort and the GEO validation 
cohort.
Functional enrichment and ppi network analysis
To explore the biological functions of the signature genes, 
Gene Ontology (GO) and Kyoto Encyclopedia of Genes 
and Genomes (KEGG) pathway enrichment analyses were 
performed using Metascape (https://metascape.org/) (Zhou 
et al. 2019), with a significance threshold of P < 0.01. A 
Protein-Protein Interaction (PPI) network was constructed 
using the STRING database (version 11.5, ​h​t​t​p​s​:​/​/​s​t​r​i​n​g​-​d​
b​.​o​r​g​/​) (Szklarczyk et al. 2019) with a minimum required 
interaction score of 0.4.
Assessment of independent prognostic factors
To evaluate whether the 9-gene signature serves as an inde­
pendent prognostic factor for breast cancer, univariate and 
multivariate Cox proportional hazards regression analyses 
were performed in the TCGA cohort. The risk score was 
analyzed alongside available clinicopathological character­
istics, including patient age, pathologic T stage, pathologic 
N stage, and ERBB2 status. The hazard ratio (HR) and 95% 
confidence interval (CI) were calculated to quantify the risk 
association. Factors with a P < 0.05 in the multivariate anal­
ysis were considered statistically significant independent 
prognostic indicators.
Immune infiltration and drug sensitivity analysis
The immune landscape was analyzed using the GSCALite 
platform 
(​h​t​t​p​:​/​/​b​i​o​i​n​f​o​.​l​i​f​e​.​h​u​s​t​.​e​d​u​.​c​n​/​w​e​b​/​G​S​C​A​L​i​t​e​/) 
(Liu et al. 2018). The correlation between the signature-
based Gene Set Variation Analysis (GSVA) score and the 
infiltration levels of diverse immune cells was evaluated. 
Furthermore, the drug sensitivity of the signature genes was 
assessed based on data from the Genomics of Drug Sen­
sitivity in Cancer (GDSC) (Yang et al. 2012) and Cancer 
Therapeutics Response Portal (CTRP) (Rees et al. 2016) 
databases via GSCALite. Spearman correlation analysis 
was performed to identify the association between gene 
expression and the half-maximal inhibitory concentration 
(IC50) of therapeutic agents.
Protein level validation
To verify the expression of the identified prognostic genes 
at the translational level, immunohistochemistry (IHC) 
staining images were retrieved from the Human Protein 
Atlas (HPA) database (https://www.proteinatlas.org/). We 
selected representative key risk genes, including MTDH, 
HSP90AA1, and VDAC1, to compare their protein expres­
sion patterns between normal breast tissues and breast inva­
sive carcinoma tissues. The staining intensity was visually 
evaluated to validate the transcriptomic analysis results.
Statistical analysis
All statistical analyses were performed usingR software 
(version 4.4.2). Differences in gene expression were ana­
lyzed using the Wilcoxon test. Survival differences were 
compared using the Log-rank test. P < 0.05 was considered 
statistically significant.

## 1.4 · ﻿Result

### 1.4.1 · ﻿Clinical characteristics of the study cohorts

expressed genes served as the initial pool for prognostic 
modeling.
Screening of prognostic autophagy-related genes 
via Kaplan-Meier survival analysis
To further narrow down the candidates to those with genu­
ine prognostic value, we performed survival analysis using 
the Kaplan-Meier Plotter database. The Log-rank test was 
utilized to statistically evaluate the significant difference in 
Overall Survival (OS) between high- and low-expression 
groups. As shown in Fig. 2, we successfully identified can­
didate genes significantly associated with patient outcomes. 
For instance, high expression of HSP90AA1 (HR = 1.51, 
P < 0.001) was identified as a significant risk factor, whereas 
TP63 (HR = 0.73, P < 0.001) functioned as a protective fac­
tor. Genes with a significant Log-rank p 0.05 were retained 
for the subsequent construction of the multivariate model.
To comprehensively screen for potential prognostic bio­
markers and maximize the sensitivity of identification, the 
‘auto select best cutoff’ algorithm was employed for single-
gene survival analysis in the Kaplan-Meier Plotter database. 
This strategy calculates all possible percentiles between the 
lower and upper quartiles and selects the threshold with the 
highest statistical significance, thereby avoiding the omis­
sion of potential candidates due to rigid cutoff values.
Construction and evaluation of a 9-gene autophagy-
related prognostic signature
To resolve multicollinearity among the prognostic can­
didates and prevent model overfitting, we employed the 
Least Absolute Shrinkage and Selection Operator (LASSO) 
Cox regression algorithm. The trajectory of regression 
Result
Clinical characteristics of the study cohorts
The comprehensive clinical annotations of the training set 
(TCGA-BRCA, n = 1083) and the external validation set 
(GSE20685, n = 102) were analyzed. In the TCGA cohort, 
the median age was 58 years, with 53.8% of patients aged 
60 years. The majority of patients were diagnosed with 
early-stage breast cancer (Stage I-II, approx. 72%), while 
Stage III and IV accounted for 23.1% and 1.8%, respec­
tively. Similarly, the external validation cohort (GSE20685) 
consisted of 102 breast cancer patients with comparable 
baseline characteristics. These clinical features were incor­
porated into the multivariate regression analysis to assess 
the independence of the prognostic signature.
Identification of differentially expressed autophagy-
related genes in breast cancer
To identify candidate biomarkers involved in breast cancer 
progression, we obtained transcriptome RNA-sequencing 
data from the TCGA database. A total of 232 ARGs were 
retrieved from the HADb database. We performed differen­
tial expression analysis between tumor and normal tissues 
using the limma algorithm. To ensure the identified genes 
possessed both statistical significance and biological mag­
nitude, stringent filtering criteria were applied (|log2FC| > 
1 and FDR < 0.05). As a result, 56 genes were identified as 
DE-ARGs, visualized in the Venn diagram (Fig. 1A). The 
expression distribution of these genes was further illustrated 
via a volcano plot (Fig. 1B), showing 28 upregulated and 28 
downregulated genes in tumor tissues. These differentially 
Fig. 1  Identification of DE-ARGs in breast cancer.A Venn diagram 
illustrating the intersection between DEGs identified in the TCGA-
BRCA cohort and ARGs retrieved from the HADb database. B Vol­
cano plot visualizing the differential expression patterns of the 56 can­
didate DE-ARGs between tumor and normal tissues

![Fig. 1](assets/images/p4_img_1.png)
*Fig. 1 Identification of DE-ARGs in breast cancer.A Venn diagram illustrating the intersection between DEGs identified in the TCGA- BRCA cohort and ARGs retrieved from the HADb database. B Vol­ cano plot visualizing the differential expression patterns of the 56 can­ didate DE-ARGs between tumor and normal tissues*

### 1.4.2 · ﻿Identification of differentially expressed autophagy-related genes in breast cancer

expressed genes served as the initial pool for prognostic 
modeling.
Screening of prognostic autophagy-related genes 
via Kaplan-Meier survival analysis
To further narrow down the candidates to those with genu­
ine prognostic value, we performed survival analysis using 
the Kaplan-Meier Plotter database. The Log-rank test was 
utilized to statistically evaluate the significant difference in 
Overall Survival (OS) between high- and low-expression 
groups. As shown in Fig. 2, we successfully identified can­
didate genes significantly associated with patient outcomes. 
For instance, high expression of HSP90AA1 (HR = 1.51, 
P < 0.001) was identified as a significant risk factor, whereas 
TP63 (HR = 0.73, P < 0.001) functioned as a protective fac­
tor. Genes with a significant Log-rank p 0.05 were retained 
for the subsequent construction of the multivariate model.
To comprehensively screen for potential prognostic bio­
markers and maximize the sensitivity of identification, the 
‘auto select best cutoff’ algorithm was employed for single-
gene survival analysis in the Kaplan-Meier Plotter database. 
This strategy calculates all possible percentiles between the 
lower and upper quartiles and selects the threshold with the 
highest statistical significance, thereby avoiding the omis­
sion of potential candidates due to rigid cutoff values.
Construction and evaluation of a 9-gene autophagy-
related prognostic signature
To resolve multicollinearity among the prognostic can­
didates and prevent model overfitting, we employed the 
Least Absolute Shrinkage and Selection Operator (LASSO) 
Cox regression algorithm. The trajectory of regression 
Result
Clinical characteristics of the study cohorts
The comprehensive clinical annotations of the training set 
(TCGA-BRCA, n = 1083) and the external validation set 
(GSE20685, n = 102) were analyzed. In the TCGA cohort, 
the median age was 58 years, with 53.8% of patients aged 
60 years. The majority of patients were diagnosed with 
early-stage breast cancer (Stage I-II, approx. 72%), while 
Stage III and IV accounted for 23.1% and 1.8%, respec­
tively. Similarly, the external validation cohort (GSE20685) 
consisted of 102 breast cancer patients with comparable 
baseline characteristics. These clinical features were incor­
porated into the multivariate regression analysis to assess 
the independence of the prognostic signature.
Identification of differentially expressed autophagy-
related genes in breast cancer
To identify candidate biomarkers involved in breast cancer 
progression, we obtained transcriptome RNA-sequencing 
data from the TCGA database. A total of 232 ARGs were 
retrieved from the HADb database. We performed differen­
tial expression analysis between tumor and normal tissues 
using the limma algorithm. To ensure the identified genes 
possessed both statistical significance and biological mag­
nitude, stringent filtering criteria were applied (|log2FC| > 
1 and FDR < 0.05). As a result, 56 genes were identified as 
DE-ARGs, visualized in the Venn diagram (Fig. 1A). The 
expression distribution of these genes was further illustrated 
via a volcano plot (Fig. 1B), showing 28 upregulated and 28 
downregulated genes in tumor tissues. These differentially 
Fig. 1  Identification of DE-ARGs in breast cancer.A Venn diagram 
illustrating the intersection between DEGs identified in the TCGA-
BRCA cohort and ARGs retrieved from the HADb database. B Vol­
cano plot visualizing the differential expression patterns of the 56 can­
didate DE-ARGs between tumor and normal tissues

### 1.4.3 · ﻿Screening of prognostic autophagy-related genes via Kaplan-Meier survival analysis

expressed genes served as the initial pool for prognostic 
modeling.
Screening of prognostic autophagy-related genes 
via Kaplan-Meier survival analysis
To further narrow down the candidates to those with genu­
ine prognostic value, we performed survival analysis using 
the Kaplan-Meier Plotter database. The Log-rank test was 
utilized to statistically evaluate the significant difference in 
Overall Survival (OS) between high- and low-expression 
groups. As shown in Fig. 2, we successfully identified can­
didate genes significantly associated with patient outcomes. 
For instance, high expression of HSP90AA1 (HR = 1.51, 
P < 0.001) was identified as a significant risk factor, whereas 
TP63 (HR = 0.73, P < 0.001) functioned as a protective fac­
tor. Genes with a significant Log-rank p 0.05 were retained 
for the subsequent construction of the multivariate model.
To comprehensively screen for potential prognostic bio­
markers and maximize the sensitivity of identification, the 
‘auto select best cutoff’ algorithm was employed for single-
gene survival analysis in the Kaplan-Meier Plotter database. 
This strategy calculates all possible percentiles between the 
lower and upper quartiles and selects the threshold with the 
highest statistical significance, thereby avoiding the omis­
sion of potential candidates due to rigid cutoff values.
Construction and evaluation of a 9-gene autophagy-
related prognostic signature
To resolve multicollinearity among the prognostic can­
didates and prevent model overfitting, we employed the 
Least Absolute Shrinkage and Selection Operator (LASSO) 
Cox regression algorithm. The trajectory of regression 
Result
Clinical characteristics of the study cohorts
The comprehensive clinical annotations of the training set 
(TCGA-BRCA, n = 1083) and the external validation set 
(GSE20685, n = 102) were analyzed. In the TCGA cohort, 
the median age was 58 years, with 53.8% of patients aged 
60 years. The majority of patients were diagnosed with 
early-stage breast cancer (Stage I-II, approx. 72%), while 
Stage III and IV accounted for 23.1% and 1.8%, respec­
tively. Similarly, the external validation cohort (GSE20685) 
consisted of 102 breast cancer patients with comparable 
baseline characteristics. These clinical features were incor­
porated into the multivariate regression analysis to assess 
the independence of the prognostic signature.
Identification of differentially expressed autophagy-
related genes in breast cancer
To identify candidate biomarkers involved in breast cancer 
progression, we obtained transcriptome RNA-sequencing 
data from the TCGA database. A total of 232 ARGs were 
retrieved from the HADb database. We performed differen­
tial expression analysis between tumor and normal tissues 
using the limma algorithm. To ensure the identified genes 
possessed both statistical significance and biological mag­
nitude, stringent filtering criteria were applied (|log2FC| > 
1 and FDR < 0.05). As a result, 56 genes were identified as 
DE-ARGs, visualized in the Venn diagram (Fig. 1A). The 
expression distribution of these genes was further illustrated 
via a volcano plot (Fig. 1B), showing 28 upregulated and 28 
downregulated genes in tumor tissues. These differentially 
Fig. 1  Identification of DE-ARGs in breast cancer.A Venn diagram 
illustrating the intersection between DEGs identified in the TCGA-
BRCA cohort and ARGs retrieved from the HADb database. B Vol­
cano plot visualizing the differential expression patterns of the 56 can­
didate DE-ARGs between tumor and normal tissues

### 1.4.4 · ﻿Construction and evaluation of a 9-gene autophagy-related prognostic signature

expressed genes served as the initial pool for prognostic 
modeling.
Screening of prognostic autophagy-related genes 
via Kaplan-Meier survival analysis
To further narrow down the candidates to those with genu­
ine prognostic value, we performed survival analysis using 
the Kaplan-Meier Plotter database. The Log-rank test was 
utilized to statistically evaluate the significant difference in 
Overall Survival (OS) between high- and low-expression 
groups. As shown in Fig. 2, we successfully identified can­
didate genes significantly associated with patient outcomes. 
For instance, high expression of HSP90AA1 (HR = 1.51, 
P < 0.001) was identified as a significant risk factor, whereas 
TP63 (HR = 0.73, P < 0.001) functioned as a protective fac­
tor. Genes with a significant Log-rank p 0.05 were retained 
for the subsequent construction of the multivariate model.
To comprehensively screen for potential prognostic bio­
markers and maximize the sensitivity of identification, the 
‘auto select best cutoff’ algorithm was employed for single-
gene survival analysis in the Kaplan-Meier Plotter database. 
This strategy calculates all possible percentiles between the 
lower and upper quartiles and selects the threshold with the 
highest statistical significance, thereby avoiding the omis­
sion of potential candidates due to rigid cutoff values.
Construction and evaluation of a 9-gene autophagy-
related prognostic signature
To resolve multicollinearity among the prognostic can­
didates and prevent model overfitting, we employed the 
Least Absolute Shrinkage and Selection Operator (LASSO) 
Cox regression algorithm. The trajectory of regression 
Result
Clinical characteristics of the study cohorts
The comprehensive clinical annotations of the training set 
(TCGA-BRCA, n = 1083) and the external validation set 
(GSE20685, n = 102) were analyzed. In the TCGA cohort, 
the median age was 58 years, with 53.8% of patients aged 
60 years. The majority of patients were diagnosed with 
early-stage breast cancer (Stage I-II, approx. 72%), while 
Stage III and IV accounted for 23.1% and 1.8%, respec­
tively. Similarly, the external validation cohort (GSE20685) 
consisted of 102 breast cancer patients with comparable 
baseline characteristics. These clinical features were incor­
porated into the multivariate regression analysis to assess 
the independence of the prognostic signature.
Identification of differentially expressed autophagy-
related genes in breast cancer
To identify candidate biomarkers involved in breast cancer 
progression, we obtained transcriptome RNA-sequencing 
data from the TCGA database. A total of 232 ARGs were 
retrieved from the HADb database. We performed differen­
tial expression analysis between tumor and normal tissues 
using the limma algorithm. To ensure the identified genes 
possessed both statistical significance and biological mag­
nitude, stringent filtering criteria were applied (|log2FC| > 
1 and FDR < 0.05). As a result, 56 genes were identified as 
DE-ARGs, visualized in the Venn diagram (Fig. 1A). The 
expression distribution of these genes was further illustrated 
via a volcano plot (Fig. 1B), showing 28 upregulated and 28 
downregulated genes in tumor tissues. These differentially 
Fig. 1  Identification of DE-ARGs in breast cancer.A Venn diagram 
illustrating the intersection between DEGs identified in the TCGA-
BRCA cohort and ARGs retrieved from the HADb database. B Vol­
cano plot visualizing the differential expression patterns of the 56 can­
didate DE-ARGs between tumor and normal tissues

### 1.4.5 · ﻿Validation of the prognostic signature in an external independent cohort

signature, ensuring balanced sample sizes in both groups for 
rigorous statistical comparison.
Validation of the prognostic signature in an external 
independent cohort
To verify the robustness and generalization ability of the 
model, we applied the same formula to an independent 
external dataset (GSE20685) from the GEO database. The 
predictive accuracy was first evaluated using ROC analy­
sis. Remarkably, the signature maintained excellent perfor­
mance with an AUC of 0.740 (Fig. 4A), suggesting that the 
model is robust across different sequencing platforms and 
populations. Consistent with the training set, the distribu­
tion of risk scores and gene expression patterns (Fig. 4B) 
confirmed that risk-associated genes were upregulated 
in high-risk patients. Although the survival difference in 
the validation cohort did not reach statistical significance 
(P = 0.141) likely due to limited sample size, a distinct trend 
of poorer survival in the high-risk group was observed 
(HR = 1.49), further supporting the validity of our signature 
(Fig. 4C).
coefficients is shown in Fig. 3A. The optimal penalty param­
eter (λ) was selected via 10-fold cross-validation (Fig. 3B, 
Table S1 and Table S2), ultimately identifying a robust 
9-gene signature (HOTAIR, VDAC1, SERPINA1, NRG1, 
MTDH, HSPA8, HSP90AA1, TP63, and DYNLT1).A risk 
score was then calculated for each patient based on the 
regression coefficients. To evaluate the clinical relevance 
of the model, patients were categorized into high- and low-
risk groups. Kaplan-Meier analysis demonstrated that the 
high-risk group had significantly poorer OS (HR = 2.28, 
P < 0.001), confirming the discriminative ability of the risk 
score (Fig. 3C). Furthermore, to assess the predictive accu­
racy (sensitivity and specificity) of the signature, we per­
formed Time-dependent ROC analysis using the timeROC 
method. The Area Under the Curve (AUC) for 1-year sur­
vival was 0.709 (Fig. 3E), indicating satisfactory predictive 
performance in the training cohort.To ensure the robustness 
and reproducibility of the prognostic model and prevent 
overfitting, patients were categorized into high- and low-
risk groups based on the median risk score. Unlike the opti­
mal cutoff used in the screening phase, the median serves as 
an unbiased and standardized threshold for the multivariate 
Fig. 2  Kaplan-Meier survival analysis of representative prognostic 
DE-ARGs in breast cancer. A–C Kaplan-Meier curves of three repre­
sentative genes identified as risk factors. D–F Kaplan-Meier curves of 
three representative genes identified as protective factors. The overall 
survival (OS) analysis was performed using the Kaplan-Meier Plotter 
database based on mRNA gene expression. Patients were stratified into 
high- and low-expression groups based on the auto-selected best cutoff 
values. The red line indicates the high-expression group, and the black 
line indicates the low-expression group
 

Fig. 4  Validation of the 9-gene prognostic signature in the indepen­
dent GEO external cohort. A Time-dependent ROC curve analysis for 
predicting 1-year survival in the GEO validation cohort. B Risk fac­
tor analysis in the validation cohort, showing the distribution of risk 
scores (top), survival status (middle), and the expression heatmap of 
the signature genes (bottom). C Kaplan-Meier survival analysis in the 
validation cohort
 
Fig. 3  Construction and evaluation of the 9-gene autophagy-related 
prognostic signature in the TCGA training cohort. A LASSO coef­
ficient profiles of the 56 candidate autophagy-related genes. Each 
curve represents the coefficient of a single gene changing with the 
penalty parameter. B Selection of the optimal penalty parameter in 
the LASSO Cox regression model using 10-fold cross-validation. The 
vertical dashed lines indicate the optimal used to define the 9-gene 
signature. C Kaplan-Meier survival analysis of Overall Survival (OS) 
between high- and low-risk groups. D Risk factor analysis illustrat­
ing the distribution of risk scores (top), the survival status of patients 
(middle, where red dots indicate death), and the expression heatmap 
of the 9 signature genes (bottom). The vertical dotted line represents 
the median risk score cutoff distinguishing high- and low-risk groups. 
E Time-dependent ROC curve for predicting 1-year survival in the 
training cohort

![Fig. 4](assets/images/p6_img_1.png)
*Fig. 4 Validation of the 9-gene prognostic signature in the indepen­ dent GEO external cohort. A Time-dependent ROC curve analysis for predicting 1-year survival in the GEO validation cohort. B Risk fac­ tor analysis in the validation cohort, showing the distribution of risk scores (top), survival status (middle), and the expression heatmap of the signature genes (bottom). C Kaplan-Meier survival analysis in the validation cohort*

![Fig. 2](assets/images/p5_img_1.jpeg)
*Fig. 2  Kaplan-Meier survival analysis of representative prognostic DE-ARGs in breast cancer. A–C Kaplan-Meier curves of three repre­ sentative genes identified as risk factors. D–F Kaplan-Meier curves of three representative genes identified as protective factors. The overall survival (OS) analysis was performed using the Kaplan-Meier Plotter database based on mRNA gene expression. Patients were stratified into high- and low-expression groups based on the auto-selected best cutoff values. The red line indicates the high-expression group, and the black line indicates the low-expression group*

![Fig. 3](assets/images/p6_img_2.png)
*Fig. 3  Construction and evaluation of the 9-gene autophagy-related prognostic signature in the TCGA training cohort. A LASSO coef­ ficient profiles of the 56 candidate autophagy-related genes. Each curve represents the coefficient of a single gene changing with the penalty parameter. B Selection of the optimal penalty parameter in the LASSO Cox regression model using 10-fold cross-validation. The between high- and low-risk groups. D Risk factor analysis illustrat­ ing the distribution of risk scores (top), the survival status of patients (middle, where red dots indicate death), and the expression heatmap of the 9 signature genes (bottom). The vertical dotted line represents the median risk score cutoff distinguishing high- and low-risk groups. E Time-dependent ROC curve for predicting 1-year survival in the*

### 1.4.6 · ﻿Functional enrichment analysis of the signature

serves as a robust validation of our model’s specificity. 
Furthermore, the network visualization of enriched terms 
(Fig.  5C) highlighted the inter-cluster relationships, elu­
cidating a potential regulatory axis connecting autophagic 
processes with immune responses.
Immune landscape characterization and drug 
sensitivity analysis
To dissect the heterogeneity of the tumor microenvironment 
(TME) driven by the prognostic signature, we evaluated 
the association between the signature-derived GSVA scores 
and immune cell infiltration patterns using the GSCALite 
platform. This analysis aimed to determine whether the 
prognostic risk is modulated by specific immune evasion 
mechanisms. As visualized in the correlation heatmap 
(Fig.  6A), the signature exhibited significant associations 
with distinct immune cell subsets in breast cancer. Notably, 
the risk score displayed a strong positive correlation with 
Th2 cells, Cytotoxic cells, and Exhausted T cells (indicated 
by red clusters), while showing a negative correlation with 
Neutrophils and Monocytes (blue clusters). The paradoxical 
enrichment of both cytotoxic and exhausted T cells suggests 
a state of immune exhaustion: although effector lympho­
cytes are recruited to the tumor site in high-risk patients, they 
likely enter a dysfunctional state, thereby failing to exert 
effective anti-tumor immunity. This immunosuppressive 
Functional enrichment analysis of the signature
To evaluate the physical connectivity and potential func­
tional crosstalk among the prognostic genes, a Protein-
Protein Interaction (PPI) network was constructed using 
the STRING database. Given that HOTAIR is a long non-
coding RNA (lncRNA) and does not encode a protein, the 
network analysis focused on the eight protein-coding genes. 
As illustrated in Fig. 5A, the topological structure of the 
network revealed a dense interaction cluster anchored by 
the molecular chaperones HSP90AA1 and HSPA8. These 
central hub nodes exhibited strong connectivity with 
VDAC1, SERPINA1, and NRG1, indicative of a coordi­
nated functional module governing protein folding and 
stress responses. Conversely, TP63 and MTDH appeared as 
isolated nodes, suggesting that these genes may exert their 
prognostic effects through independent mechanisms distinct 
from the chaperone complex.To further validate the biologi­
cal relevance of the signature and decipher the underlying 
signaling pathways, we performed functional enrichment 
analysis using Metascape. This step aimed to verify whether 
the identified genes effectively represent autophagy-specific 
alterations. The results confirmed that the prognostic sig­
nature is intrinsically linked to autophagy regulation. As 
shown in Fig. 5B, “Selective autophagy” (R-HSA-9663891) 
emerged as the most significantly enriched ontology term, 
followed by “Neutrophil degranulation” and “Epithelial 
cell differentiation.” The dominance of selective autophagy 
Fig. 5  Protein-Protein Interaction (PPI) network and functional enrich­
ment analysis of the prognostic signature. A PPI network of the 8 pro­
tein-coding signature genes constructed using the STRING database. B 
Bar graph of the top enriched biological processes and pathways iden­
tified by Metascape analysis. C Network visualization of the enriched 
ontology terms, illustrating the inter-cluster relationships and the close 
functional connection between autophagy and immune-related pro­
cesses. Isolated nodes in the PPI network indicate proteins that do not 
show direct interactions with the main cluster (confidence score > 0.4), 
suggesting they may function through independent pathways

![Fig. 5](assets/images/p7_img_1.png)
*Fig. 5 Protein-Protein Interaction (PPI) network and functional enrich­ ment analysis of the prognostic signature. A PPI network of the 8 pro­ tein-coding signature genes constructed using the STRING database. B Bar graph of the top enriched biological processes and pathways iden­ tified by Metascape analysis. C Network visualization of the enriched ontology terms, illustrating the inter-cluster relationships and the close functional connection between autophagy and immune-related pro­ cesses. Isolated nodes in the PPI network indicate proteins that do not show direct interactions with the main cluster (confidence score > 0.4), suggesting they may function through independent pathways*

### 1.4.7 · ﻿Immune landscape characterization and drug sensitivity analysis

serves as a robust validation of our model’s specificity. 
Furthermore, the network visualization of enriched terms 
(Fig.  5C) highlighted the inter-cluster relationships, elu­
cidating a potential regulatory axis connecting autophagic 
processes with immune responses.
Immune landscape characterization and drug 
sensitivity analysis
To dissect the heterogeneity of the tumor microenvironment 
(TME) driven by the prognostic signature, we evaluated 
the association between the signature-derived GSVA scores 
and immune cell infiltration patterns using the GSCALite 
platform. This analysis aimed to determine whether the 
prognostic risk is modulated by specific immune evasion 
mechanisms. As visualized in the correlation heatmap 
(Fig.  6A), the signature exhibited significant associations 
with distinct immune cell subsets in breast cancer. Notably, 
the risk score displayed a strong positive correlation with 
Th2 cells, Cytotoxic cells, and Exhausted T cells (indicated 
by red clusters), while showing a negative correlation with 
Neutrophils and Monocytes (blue clusters). The paradoxical 
enrichment of both cytotoxic and exhausted T cells suggests 
a state of immune exhaustion: although effector lympho­
cytes are recruited to the tumor site in high-risk patients, they 
likely enter a dysfunctional state, thereby failing to exert 
effective anti-tumor immunity. This immunosuppressive 
Functional enrichment analysis of the signature
To evaluate the physical connectivity and potential func­
tional crosstalk among the prognostic genes, a Protein-
Protein Interaction (PPI) network was constructed using 
the STRING database. Given that HOTAIR is a long non-
coding RNA (lncRNA) and does not encode a protein, the 
network analysis focused on the eight protein-coding genes. 
As illustrated in Fig. 5A, the topological structure of the 
network revealed a dense interaction cluster anchored by 
the molecular chaperones HSP90AA1 and HSPA8. These 
central hub nodes exhibited strong connectivity with 
VDAC1, SERPINA1, and NRG1, indicative of a coordi­
nated functional module governing protein folding and 
stress responses. Conversely, TP63 and MTDH appeared as 
isolated nodes, suggesting that these genes may exert their 
prognostic effects through independent mechanisms distinct 
from the chaperone complex.To further validate the biologi­
cal relevance of the signature and decipher the underlying 
signaling pathways, we performed functional enrichment 
analysis using Metascape. This step aimed to verify whether 
the identified genes effectively represent autophagy-specific 
alterations. The results confirmed that the prognostic sig­
nature is intrinsically linked to autophagy regulation. As 
shown in Fig. 5B, “Selective autophagy” (R-HSA-9663891) 
emerged as the most significantly enriched ontology term, 
followed by “Neutrophil degranulation” and “Epithelial 
cell differentiation.” The dominance of selective autophagy 
Fig. 5  Protein-Protein Interaction (PPI) network and functional enrich­
ment analysis of the prognostic signature. A PPI network of the 8 pro­
tein-coding signature genes constructed using the STRING database. B 
Bar graph of the top enriched biological processes and pathways iden­
tified by Metascape analysis. C Network visualization of the enriched 
ontology terms, illustrating the inter-cluster relationships and the close 
functional connection between autophagy and immune-related pro­
cesses. Isolated nodes in the PPI network indicate proteins that do not 
show direct interactions with the main cluster (confidence score > 0.4), 
suggesting they may function through independent pathways
 

(IC50 values) using the CTRP database. The objective of 
this analysis was to identify potential resistance mecha­
nisms and therapeutic vulnerabilities. The bubble heatmap 
(Fig. 6B) revealed a polarized landscape of drug response. 
Genes such as SERPINA1 and NRG1 showed broad positive 
feature provides a plausible biological explanation for the 
poorer prognosis observed in the high-risk group.
Furthermore, to translate these molecular findings into 
clinical therapeutic strategies, we assessed the correlation 
between signature gene expression and drug sensitivity 
Fig. 6  Immune landscape characterization and drug sensitivity analysis. 
A Heatmap illustrating the Spearman correlation between the prognos­
tic signature (Risk Score) and immune cell infiltration levels in breast 
cancer (GSCALite). Red blocks indicate positive correlations, while 
blue blocks indicate negative correlations. B Bubble heatmap showing 
the correlation between the expression of the 9 signature genes and 
drug sensitivity (IC50 values) from the CTRP database. Blue bubbles 
represent negative correlations (higher gene expression is associated 
with lower IC50, indicating higher drug sensitivity), while red bubbles 
represent positive correlations (drug resistance)

![Fig. 6](assets/images/p8_img_1.png)
*Fig. 6  Immune landscape characterization and drug sensitivity analysis. A Heatmap illustrating the Spearman correlation between the prognos­ tic signature (Risk Score) and immune cell infiltration levels in breast cancer (GSCALite). Red blocks indicate positive correlations, while blue blocks indicate negative correlations. B Bubble heatmap showing the correlation between the expression of the 9 signature genes and drug sensitivity (IC50 values) from the CTRP database. Blue bubbles represent negative correlations (higher gene expression is associated with lower IC50, indicating higher drug sensitivity), while red bubbles represent positive correlations (drug resistance)*

### 1.4.8 · ﻿Evaluation of the independent prognostic value of the signature

P < 0.001). Importantly, after adjusting for confounding fac­
tors in the multivariate analysis, the risk score remained a 
robust and independent predictor of prognosis (HR = 2.718, 
95% CI = 1.891–3.907, P < 0.001). These findings suggest 
that the prognostic value of our signature is independent of 
traditional clinicopathological features.
Construction of a prognostic nomogram based on 
the signature
To facilitate the clinical application of our 9-gene signature, 
we constructed a prognostic nomogram to quantify the pre­
dicted survival probability for individual patients (Fig. 8A). 
In this model, the risk score is mapped to a specific point 
value on the “Points” scale. By locating the patient’s risk 
score and identifying the corresponding position on the 
“Total Points” axis, the estimated 1-, 3-, and 5-year overall 
survival (OS) probabilities can be determined. As shown in 
the nomogram, a higher risk score corresponds to a lower 
survival probability. Furthermore, the predictive accuracy 
of the nomogram was evaluated using calibration curves 
(Fig. 8B). The calibration plots for 1-, 3-, and 5-year OS 
correlations with IC50 values (red bubbles), implying that 
their upregulation may confer multidrug resistance. Con­
versely, MTDH exhibited significant negative correlations 
with the IC50 of several agents (blue bubbles), including 
Vincristine, Vorinostat, and Gemcitabine. These findings 
suggest a stratified therapeutic approach: while high-risk 
tumors driven by MTDH expression may be refractory 
to standard treatments, they could potentially be targeted 
effectively with regimens containing these specific agents.
Evaluation of the independent prognostic value of 
the signature
To determine whether the 9-gene signature could serve as 
an independent prognostic factor for breast cancer patients, 
we performed univariate and multivariate Cox regression 
analyses in the TCGA cohort. The analysis included the 
risk score and accessible clinical characteristics, such as 
Pathologic T stage, Pathologic N stage, and ERBB2 status. 
As shown in Table S3 and Fig. 7, the univariate analysis 
indicated that the risk score was significantly associated 
with overall survival (HR = 2.718, 95% CI = 1.891–3.907, 
Fig. 7  Independent prognostic analysis. Forest plot visualizing the multivariate Cox regression analysis results. The risk score (P < 0.001) and N 
stage serve as independent prognostic factors for overall survival in breast cancer patients

![Fig. 7](assets/images/p9_img_1.png)
*Fig. 7 Independent prognostic analysis. Forest plot visualizing the multivariate Cox regression analysis results. The risk score (P < 0.001) and N stage serve as independent prognostic factors for overall survival in breast cancer patients*

### 1.4.9 · ﻿Construction of a prognostic nomogram based on the signature

P < 0.001). Importantly, after adjusting for confounding fac­
tors in the multivariate analysis, the risk score remained a 
robust and independent predictor of prognosis (HR = 2.718, 
95% CI = 1.891–3.907, P < 0.001). These findings suggest 
that the prognostic value of our signature is independent of 
traditional clinicopathological features.
Construction of a prognostic nomogram based on 
the signature
To facilitate the clinical application of our 9-gene signature, 
we constructed a prognostic nomogram to quantify the pre­
dicted survival probability for individual patients (Fig. 8A). 
In this model, the risk score is mapped to a specific point 
value on the “Points” scale. By locating the patient’s risk 
score and identifying the corresponding position on the 
“Total Points” axis, the estimated 1-, 3-, and 5-year overall 
survival (OS) probabilities can be determined. As shown in 
the nomogram, a higher risk score corresponds to a lower 
survival probability. Furthermore, the predictive accuracy 
of the nomogram was evaluated using calibration curves 
(Fig. 8B). The calibration plots for 1-, 3-, and 5-year OS 
correlations with IC50 values (red bubbles), implying that 
their upregulation may confer multidrug resistance. Con­
versely, MTDH exhibited significant negative correlations 
with the IC50 of several agents (blue bubbles), including 
Vincristine, Vorinostat, and Gemcitabine. These findings 
suggest a stratified therapeutic approach: while high-risk 
tumors driven by MTDH expression may be refractory 
to standard treatments, they could potentially be targeted 
effectively with regimens containing these specific agents.
Evaluation of the independent prognostic value of 
the signature
To determine whether the 9-gene signature could serve as 
an independent prognostic factor for breast cancer patients, 
we performed univariate and multivariate Cox regression 
analyses in the TCGA cohort. The analysis included the 
risk score and accessible clinical characteristics, such as 
Pathologic T stage, Pathologic N stage, and ERBB2 status. 
As shown in Table S3 and Fig. 7, the univariate analysis 
indicated that the risk score was significantly associated 
with overall survival (HR = 2.718, 95% CI = 1.891–3.907, 
Fig. 7  Independent prognostic analysis. Forest plot visualizing the multivariate Cox regression analysis results. The risk score (P < 0.001) and N 
stage serve as independent prognostic factors for overall survival in breast cancer patients

### 1.4.10 · ﻿Validation of protein expression patterns using the HPA database

breast cancer tissues compared to normal tissues. Specifi­
cally, normal breast tissues exhibited weak or non-detected 
staining (mostly visible in adipocytes or sparse ductal cells), 
whereas tumor tissues displayed moderate to strong brown 
staining intensity, indicating high protein abundance. These 
findings are consistent with our mRNA differential expres­
sion analysis, confirming that these autophagy-related genes 
are overexpressed at the protein level in breast cancer.
Discussion
In this study, we aimed to address the challenge of biologi­
cal heterogeneity in breast cancer (BRCA) by construct­
ing a robust prognostic tool. By systematically integrating 
demonstrated excellent agreement between the nomogram-
predicted probabilities and the actual observed survival 
rates, with the curves closely tracking the ideal 45-degree 
diagonal line. This indicates that the nomogram based on 
our 9-gene signature possesses high reliability and calibra­
tion accuracy.
Validation of protein expression patterns using the 
HPA database
To further corroborate the biological significance of our 
signature, we validated the protein expression levels of 
key risk genes using IHC data from the HPA database. As 
illustrated in Fig. 9, the protein expression levels of MTDH, 
HSP90AA1, and VDAC1 were markedly upregulated in 
Fig. 9  Protein level validation 
of key signature genes. Repre­
sentative immunohistochemistry 
(IHC) staining images of MTDH, 
HSP90AA1, and VDAC1 in 
normal breast tissues (upper 
panel) and breast cancer tissues 
(lower panel). The images were 
retrieved from the Human Protein 
Atlas (HPA) database. The results 
demonstrate that the protein 
expression of these risk genes 
is significantly higher in tumor 
tissues (strong brown staining) 
compared to normal tissues 
(weak or negative staining)
 
Fig. 8  Construction of a prognostic nomogram. A nomogram estab­
lished based on the 9-gene risk score to predict the 1-, 3-, and 5-year 
overall survival probability of breast cancer patients. The “Points” 
scale allows for the conversion of the risk score into a quantitative 
prognostic metric. B Calibration curves of the nomogram for predict­
ing 1-, 3-, and 5-year survival (bootstrap method with 1000 resamples). 
The x-axis represents the predicted survival probability, and the y-axis 
represents the actual observed survival probability. The diagonal line 
represents the ideal prediction

![breast cancer tissues compared to normal tissues. Specifi­ cally, normal breast tissues exhibited weak or non-detected staining (mostly visible in adipocytes or sparse ductal cells), whereas tumor tissues displayed moderate to strong brown agreement between the nomogram- the actual observed survival tracking the ideal 45-degree that the nomogram based on](assets/images/p10_img_1.jpeg)
*breast cancer tissues compared to normal tissues. Specifi­ cally, normal breast tissues exhibited weak or non-detected staining (mostly visible in adipocytes or sparse ductal cells), whereas tumor tissues displayed moderate to strong brown agreement between the nomogram- the actual observed survival tracking the ideal 45-degree that the nomogram based on*

![Construction of a prognostic nomogram. A nomogram estab­ the 9-gene risk score to predict the 1-, 3-, and 5-year probability of breast cancer patients. The “Points” the conversion of the risk score into a quantitative B Calibration curves of the nomogram for predict­ ing 1-, 3-, and 5-year survival (bootstrap method with The x-axis represents the predicted survival probability, represents the actual observed survival probability. represents the ideal prediction](assets/images/p10_img_2.jpeg)
*Construction of a prognostic nomogram. A nomogram estab­ the 9-gene risk score to predict the 1-, 3-, and 5-year probability of breast cancer patients. The “Points” the conversion of the risk score into a quantitative B Calibration curves of the nomogram for predict­ ing 1-, 3-, and 5-year survival (bootstrap method with The x-axis represents the predicted survival probability, represents the actual observed survival probability. represents the ideal prediction*

## 1.5 · ﻿Discussion

breast cancer tissues compared to normal tissues. Specifi­
cally, normal breast tissues exhibited weak or non-detected 
staining (mostly visible in adipocytes or sparse ductal cells), 
whereas tumor tissues displayed moderate to strong brown 
staining intensity, indicating high protein abundance. These 
findings are consistent with our mRNA differential expres­
sion analysis, confirming that these autophagy-related genes 
are overexpressed at the protein level in breast cancer.
Discussion
In this study, we aimed to address the challenge of biologi­
cal heterogeneity in breast cancer (BRCA) by construct­
ing a robust prognostic tool. By systematically integrating 
demonstrated excellent agreement between the nomogram-
predicted probabilities and the actual observed survival 
rates, with the curves closely tracking the ideal 45-degree 
diagonal line. This indicates that the nomogram based on 
our 9-gene signature possesses high reliability and calibra­
tion accuracy.
Validation of protein expression patterns using the 
HPA database
To further corroborate the biological significance of our 
signature, we validated the protein expression levels of 
key risk genes using IHC data from the HPA database. As 
illustrated in Fig. 9, the protein expression levels of MTDH, 
HSP90AA1, and VDAC1 were markedly upregulated in 
Fig. 9  Protein level validation 
of key signature genes. Repre­
sentative immunohistochemistry 
(IHC) staining images of MTDH, 
HSP90AA1, and VDAC1 in 
normal breast tissues (upper 
panel) and breast cancer tissues 
(lower panel). The images were 
retrieved from the Human Protein 
Atlas (HPA) database. The results 
demonstrate that the protein 
expression of these risk genes 
is significantly higher in tumor 
tissues (strong brown staining) 
compared to normal tissues 
(weak or negative staining)
 
Fig. 8  Construction of a prognostic nomogram. A nomogram estab­
lished based on the 9-gene risk score to predict the 1-, 3-, and 5-year 
overall survival probability of breast cancer patients. The “Points” 
scale allows for the conversion of the risk score into a quantitative 
prognostic metric. B Calibration curves of the nomogram for predict­
ing 1-, 3-, and 5-year survival (bootstrap method with 1000 resamples). 
The x-axis represents the predicted survival probability, and the y-axis 
represents the actual observed survival probability. The diagonal line 
represents the ideal prediction
 
 

microenvironment characterization, and precision chemo­
therapy. We observed a distinct “immune-exhausted” land­
scape in high-risk patients, characterized by the enrichment 
of exhausted T cells and depletion of neutrophils(DeNardo 
and Coussens 2007; Wherry 2011). While previous lit­
erature suggests that dysregulated autophagy can impair 
antigen presentation (Yamamoto et al. 2020; Wang et al. 
2025), we further propose that a “metabolic competition” 
mechanism may drive this immunosuppression. Genes such 
as HSP90AA1 stabilize proteins to support high metabolic 
rates in tumor cells under stress. The hyper-activation of 
autophagy likely enhances tumor metabolic fitness, lead­
ing to the rapid depletion of glucose and essential nutrients 
in the tumor microenvironment (TME). Since effector T 
cells are highly dependent on glycolysis for function, this 
nutrient-deprived environment forces them into metabolic 
insufficiency, thereby driving them toward an exhausted 
phenotype (Yi et al. 2010). At the molecular level, our 
signature captures complex regulatory networks, exempli­
fied by the inclusion of HOTAIR, a long non-coding RNA. 
Its inclusion in the Human Autophagy Database is justi­
fied by its role as a critical upstream regulator rather than 
a direct executioner. Accumulating evidence indicates that 
lncRNAs function as competing endogenous RNAs to mod­
ulate autophagy. Specifically in breast cancer, HOTAIR has 
been reported to sponge miR-20a-5p, thereby upregulating 
HMGB1 and ATG7, key promoters of autophagy flux (Xue 
et al. 2016). Furthermore, HOTAIR-mediated autophagy 
promotes cell survival under metabolic stress, linking epi­
genetic regulation directly to the chemoresistance observed 
in high-risk patients (Li et al. 2019). Thus, HOTAIR serves 
as a vital scaffold orchestrating the autophagy-related net­
work, validating its significance in our model.
Beyond phenotypic characterization, we translated these 
findings into clinical applications by identifying therapeutic 
vulnerabilities (Barretina et al. 2012). While high-risk genes 
like SERPINA1 were associated with broad resistance (Raj­
apakse et al. 2018), we intriguingly found that high MTDH 
expression correlates with increased sensitivity to Vincris­
tine and Gemcitabine (Song et al. 2015; Yang et al. 2018). 
This finding initially appears paradoxical given MTDH’s 
established role as an oncogene promoting multidrug resis­
tance. However, this discrepancy can be explained by “col­
lateral sensitivity.” Vincristine specifically targets cells in 
the M-phase; thus, while MTDH drives aggressive prolifer­
ation and a high mitotic index, it inadvertently renders these 
rapidly dividing cells more vulnerable to anti-mitotic agents 
(Dumontet and Jordan 2010). This suggests that MTDH 
could serve as a dual biomarker: predicting poor prognosis 
while simultaneously indicating responsiveness to specific 
regimens. This discovery highlights the unique potential of 
our signature to guide personalized treatment, contrasting 
transcriptomic profiles from TCGA and GEO databases, 
we successfully established a novel 9-gene autophagy-
related signature via LASSO Cox regression analysis. Our 
model demonstrated superior prognostic capacity, effec­
tively stratifying patients into distinct risk groups. Specifi­
cally, the high-risk group exhibited a significantly poorer 
Overall Survival (OS) in the training cohort, with a Haz­
ard Ratio of 2.28 (P < 0.001). Importantly, the robustness 
of this signature was confirmed in an independent external 
validation cohort, where it achieved a high Area Under the 
Curve (AUC) of 0.740 for 1-year survival, indicating excel­
lent generalization ability compared to traditional clinico­
pathological indicators. These quantitative results confirm 
that our autophagy-based signature serves as a reliable bio­
marker for risk stratification in BRCA patients.
Our study provides new insights into the molecular 
mechanisms of BRCA by identifying specific ARGs linked 
to prognosis. Consistent with previous findings, we iden­
tified HOTAIR and MTDH as key risk factors. HOTAIR, 
a well-known lncRNA, has been reported to promote epi­
thelial-mesenchymal transition (EMT) and metastasis by 
remodeling chromatin state (Gupta et al. 2010; Mozdarani 
et al. 2020). Similarly, MTDH is known to facilitate multi-
drug resistance and angiogenesis in aggressive breast can­
cers (Hu et al. 2009). However, unlike previous studies that 
focused on single biomarkers (Zheng et al. 2018), our study 
innovatively constructs a multi-gene panel that captures the 
synergistic effects of these genes. Functional enrichment 
analysis revealed that our risk score is intimately associ­
ated with “selective autophagy” pathways (Gatica et al. 
2018). This suggests that high-risk tumors may utilize spe­
cific autophagic machinery to recycle nutrients and survive 
metabolic stress, a mechanism that has been increasingly 
recognized as a hallmark of advanced malignancy (Jin et al. 
2022). It is well-established that autophagy plays a dual role 
in cancer, functioning as either a tumor suppressor (cyto­
toxic) or a survival mechanism (cytoprotective) depend­
ing on the context. Our results indicate that the high-risk 
score is strongly associated with poor survival and chemo­
resistance, suggesting that our signature primarily captures 
‘cytoprotective autophagy.’ In this scenario, upregulated 
autophagy genes help tumor cells mitigate metabolic stress 
and recycle nutrients within the hypoxic tumor microenvi­
ronment, thereby shielding them from apoptotic cell death. 
This maladaptive survival mechanism explains why high-
risk patients exhibit aggressive clinical features and refrac­
tory responses to standard therapies. By systematically 
linking these genes to selective autophagy, our model offers 
a more comprehensive biological interpretation than single-
gene studies.
A major novelty of this study lies in bridging the criti­
cal gap between autophagy-based prognosis, immune

## 1.6 · ﻿Conclusion

### 1.6.1 · ﻿Study limitations

Study limitations
Our study has several limitations. First, the retrospective 
design based on public databases (TCGA and GEO) may 
introduce inherent selection bias. Large-scale, multi-cen­
ter prospective cohorts are required to further validate the 
clinical utility and robustness of our signature. Second, we 
acknowledge a statistical discrepancy in the external vali­
dation cohort, where the model showed robust predictive 
accuracy (AUC = 0.740) but marginal survival stratification 
significance (P = 0.141). This is likely attributable to the 
limited sample size and platform heterogeneity (RNA-seq 
vs. Microarray) in the GSE20685 dataset. However, the dis­
tinct separation trend in survival curves and the substantial 
Hazard Ratio (HR = 1.49) suggest genuine generalization 
potential that warrants verification in larger cohorts. Finally, 
our findings rely primarily on bioinformatic analyses. The 
lack of in vitro or in vivo experimental validation restricts 
our mechanistic understanding. Future studies should incor­
porate wet-lab experiments to verify specific molecular 
mechanisms and employ alternative algorithms to cross-
validate the identified immune landscape features.
Supplementary 
Information  The 
online 
version 
contains 
supplementary material available at ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​0​7​/​s​1​3​2​0​5​-​0​
2​6​-​0​4​7​5​6​-​5.
Acknowledgements  This work was supported by The medical and 
health research project of Zhejiang province (grant No. 2024KY1482).
Author contributions  Jianan Zhang: Conceptualization, Data cura­
tion, Formal analysis, Methodology, Software, Visualization, Writing 
original draft. Yijun Wang: Data curation, Validation, Writing review 
& editing. Mengsha Zou: Conceptualization, Funding acquisition, 
Project administration, Supervision, Writing review & editing. All au­
thors have contributed to the preparation of this manuscript and have 
approved its submission for publication. The order of authors listed in 
the manuscript has been agreed upon by all authors.
Data availability  The raw data supporting the conclusions of this arti­
cle will be made available by the authors, without undue reservation, 
to any qualified researcher.
Declarations
Conflict of interest  The authors declare no conflict of interest related 
to this article.
Open Access   This article is licensed under a Creative Commons 
Attribution 4.0 International License, which permits use, sharing, 
adaptation, distribution and reproduction in any medium or format, 
as long as you give appropriate credit to the original author(s) and the 
source, provide a link to the Creative Commons licence, and indicate 
if changes were made. The images or other third party material in this 
article are included in the article’s Creative Commons licence, unless 
indicated otherwise in a credit line to the material. If material is not 
included in the article’s Creative Commons licence and your intended 
use is not permitted by statutory regulation or exceeds the permitted 
sharply with existing models that lack actionable therapeu­
tic guidance (Deng et al. 2021; Yu et al. 2024a).
Despite these promising findings, several limitations 
should be acknowledged. First, this is a retrospective study 
based on public databases; prospective clinical trials are 
needed to validate the signature’s clinical utility. Second, 
although the validation cohort showed a clear risk trend 
and high AUC, larger external cohorts are required to sta­
tistically confirm the survival differences. Finally, while we 
propose metabolic and molecular mechanisms (such as the 
MTDH-Vincristine axis and metabolic competition), further 
experimental investigations—including in vitro and in vivo 
studies—are warranted to fully elucidate how these 9 genes 
synergistically regulate selective autophagy and immune 
exhaustion.
In summary, this study constructed a robust 9-gene 
autophagy-related signature that effectively predicts sur­
vival, delineates the immune exhaustion landscape, and 
identifies therapeutic vulnerabilities in breast cancer. How­
ever, as a retrospective study, inherent selection biases exist, 
and the molecular mechanisms underlying the MTDH-Vin­
cristine interaction require further experimental verification. 
To bridge the gap between bench and bedside, future trans­
lational efforts should focus on developing a standardized 
9-gene qRT-PCR diagnostic assay. This cost-effective tool 
could be integrated into routine pathology to complement 
TNM staging for refining prognosis and guiding chemo­
therapy selection based on MTDH expression. Although 
prospective multi-center validation is still warranted, our 
findings lay a solid foundation for developing autophagy-
targeted precision medicine strategies.
Conclusion
This study addresses the critical challenge of biological 
heterogeneity in breast cancer by constructing a clinically 
actionable 9-gene autophagy-related signature. Our findings 
bridge the gap between autophagic regulation and tumor 
immunity, revealing that high-risk tumors are character­
ized by a distinct “immune-exhausted” microenvironment 
driven by selective autophagy. Importantly, we translated 
these molecular features into therapeutic opportunities, 
identifying MTDH as a potential precision marker for tar­
geting multidrug-resistant tumors with specific agents like 
Vincristine and Gemcitabine. Collectively, this signature 
serves not merely as a prognostic tool but as a comprehen­
sive guide for optimizing risk assessment and personalizing 
therapeutic interventions in the era of precision medicine.

## 1.7 · ﻿References

Grunfeld E (2005) Clinical practice guidelines for the care and treat­
ment of breast cancer: follow-up after treatment for breast cancer 
(summary of the 2005 update). Can Med Assoc J 172:1319–1320. ​
h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​5​0​3​/​c​m​a​j​.​0​4​5​0​6​2
Gu Y, Li P, Peng F et al (2016) Autophagy-related prognostic signature 
for breast cancer. Mol Carcinog 55:292–299. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​
0​0​2​/​m​c​.​2​2​2​7​8
Gupta RA, Shah N, Wang KC et al (2010) Long non-coding RNA 
HOTAIR reprograms chromatin state to promote cancer metasta­
sis. Nature 464:1071–1076. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​n​a​t​u​r​e​0​8​9​7​5
Győrffy B (2021) Survival analysis across the entire transcriptome 
identifies biomarkers with the highest prognostic power in breast 
cancer. Comput Struct Biotechnol J 19:4101–4109. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​
g​/​1​0​.​1​0​1​6​/​j​.​c​s​b​j​.​2​0​2​1​.​0​7​.​0​1​4
Hu G, Chong RA, Yang Q et al (2009) MTDH Activation by 8q22 
Genomic Gain Promotes Chemoresistance and Metastasis of 
Poor-Prognosis Breast Cancer. Cancer Cell 15:9–20. ​h​t​t​p​s​:​/​/​d​o​i​.​o​
r​g​/​1​0​.​1​0​1​6​/​j​.​c​c​r​.​2​0​0​8​.​1​1​.​0​1​3
Jin Z, Sun X, Wang Y et al (2022) Regulation of autophagy fires up the 
cold tumor microenvironment to improve cancer immunotherapy. 
Front Immunol 13:1018903. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​8​9​/​f​i​m​m​u​.​2​0​2​2​
.​1​0​1​8​9​0​3
Klionsky DJ, Abdel-Aziz AK, Abdelfatah S et al (2021) Guidelines 
for the use and interpretation of assays for monitoring autophagy 
(4th edition)1. Autophagy 17:1–382. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​8​0​/​1​5​5​
4​8​6​2​7​.​2​0​2​0​.​1​7​9​7​2​8​0
Li Z, Qian J, Li J, Zhu C (2019) Knockdown of lncRNA–HOTAIR 
downregulates the drug–resistance of breast cancer cells to doxo­
rubicin via the PI3K/AKT/mTOR signaling pathway. Exp Ther 
Med. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​8​9​2​/​e​t​m​.​2​0​1​9​.​7​6​2​9
Liang XH, Jackson S, Seaman M et al (1999) Induction of autophagy 
and inhibition of tumorigenesis by beclin 1. Nature 402:672–676. 
Lin H, Zelterman D (2002) Modeling Survival Data: Extending the 
Cox Model. Technometrics 44:85–86. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​1​9​8​/​t​e​
c​h​.​2​0​0​2​.​s​6​5​6
Liu C-J, Hu F-F, Xia M-X et al (2018) GSCALite: a web server for 
gene set cancer analysis. Bioinformatics 34:3771–3772. ​h​t​t​p​s​:​/​/​d​
o​i​.​o​r​g​/​1​0​.​1​0​9​3​/​b​i​o​i​n​f​o​r​m​a​t​i​c​s​/​b​t​y​4​1​1
Luo T, Fu J, Xu A et al (2016) PSMD10/gankyrin induces autophagy to 
promote tumor progression through cytoplasmic interaction with 
ATG7 and nuclear transactivation of ATG7 expression. Autoph­
agy 12:1355–1371. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​8​0​/​1​5​5​4​8​6​2​7​.​2​0​1​5​.​1​0​3​4​
4​0​5
Meehan J, Gray M, Martínez-Pérez C et al (2020) Precision Medicine 
and the Role of Biomarkers of Radiotherapy Response in Breast 
Cancer. Front Oncol 10:628. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​8​9​/​f​o​n​c​.​2​0​2​0​.​0​
0​6​2​8
Moussay E, Kaoma T, Baginska J et al (2011) The acquisition of 
resistance to TNFα in breast cancer cells is associated with con­
stitutive activation of autophagy as revealed by a transcriptome 
analysis using a custom microarray. Autophagy 7:760–770. ​h​t​t​p​s​
:​/​/​d​o​i​.​o​r​g​/​1​0​.​4​1​6​1​/​a​u​t​o​.​7​.​7​.​1​5​4​5​4
Mozdarani H, Ezzatizadeh V, Rahbar Parvaneh R (2020) The emerg­
ing role of the long non-coding RNA HOTAIR in breast cancer 
development and treatment. J Transl Med 18:152. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​
1​0​.​1​1​8​6​/​s​1​2​9​6​7​-​0​2​0​-​0​2​3​2​0​-​0
Rajapakse VN, Luna A, Yamade M et al (2018) CellMinerCDB for 
Integrative Cross-Database Genomics and Pharmacogenomics 
Analyses of Cancer Cell Lines. iScience 10:247–264. ​h​t​t​p​s​:​/​/​d​o​
i​.​o​r​g​/​1​0​.​1​0​1​6​/​j​.​i​s​c​i​.​2​0​1​8​.​1​1​.​0​2​9
Rees MG, Seashore-Ludlow B, Cheah JH et al (2016) Correlating 
chemical sensitivity and basal gene expression reveals mecha­
nism of action. Nat Chem Biol 12:109–116. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​
0​3​8​/​n​c​h​e​m​b​i​o​.​1​9​8​6
use, you will need to obtain permission directly from the copyright 
holder. To view a copy of this licence, visit ​h​t​t​p​:​/​/​c​r​e​a​t​i​v​e​c​o​m​m​o​n​s​.​o​
r​g​/​l​i​c​e​n​s​e​s​/​b​y​/​4​.​0​/.
References
Afzal MZ, Vahdat LT (2024) Evolving Management of Breast Cancer 
in the Era of Predictive Biomarkers and Precision Medicine. JPM 
14:719. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​9​0​/​j​p​m​1​4​0​7​0​7​1​9
Baliu-Piqué M, Pandiella A, Ocana A (2020) Breast Cancer Heteroge­
neity and Response to Novel Therapeutics. Cancers 12:3271. ​h​t​t​p​
s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​9​0​/​c​a​n​c​e​r​s​1​2​1​1​3​2​7​1
Barretina J, Caponigro G, Stransky N et al (2012) The Cancer Cell 
Line Encyclopedia enables predictive modelling of anticancer 
drug sensitivity. Nature 483:603–607. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​n​
a​t​u​r​e​1​1​0​0​3
Barrett T, Wilhite SE, Ledoux P et al (2012) NCBI GEO: archive 
for functional genomics data sets—update. Nucleic Acids Res 
41:D991–D995. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​9​3​/​n​a​r​/​g​k​s​1​1​9​3
Benson JR (2003) The TNM staging system and breast cancer. Lancet 
Oncol 4:56–60. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​1​6​/​S​1​4​7​0​-​2​0​4​5​(​0​3​)​0​0​9​6​1​-​6
Blanche P, Dartigues J, Jacqmin-Gadda H (2013) Estimating and com­
paring time‐dependent areas under receiver operating character­
istic curves for censored event times with competing risks. Stat 
Med 32:5381–5397. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​0​2​/​s​i​m​.​5​9​5​8
Chavez-Dominguez R, Perez-Medina M, Lopez-Gonzalez JS et 
al (2020) The Double-Edge Sword of Autophagy in Cancer: 
From Tumor Suppression to Pro-tumor Activity. Front Oncol 
10:578418. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​8​9​/​f​o​n​c​.​2​0​2​0​.​5​7​8​4​1​8
Clark CA, Gupta HB, Curiel TJ (2017) Tumor cell-intrinsic CD274/
PD-L1: A novel metabolic balancing act with clinical potential. 
Autophagy 13:987–988. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​8​0​/​1​5​5​4​8​6​2​7​.​2​0​1​7​
.​1​2​8​0​2​2​3
Cserni G, Chmielik E, Cserni B, Tot T (2018) The new TNM-based 
staging of breast cancer. Virchows Arch 472:697–703. ​h​t​t​p​s​:​/​/​d​o​i​
.​o​r​g​/​1​0​.​1​0​0​7​/​s​0​0​4​2​8​-​0​1​8​-​2​3​0​1​-​9
DeNardo DG, Coussens LM (2007) Inflammation and breast cancer. 
Balancing immune response: crosstalk between adaptive and 
innate immune cells during breast cancer progression. Breast 
Cancer Res 9:212. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​1​8​6​/​b​c​r​1​7​4​6
Deng Y, Zhang F, Sun Z-G, Wang S (2021) Development and Vali­
dation of a Prognostic Signature Associated With Tumor Micro­
environment Based on Autophagy-Related lncRNA Analysis in 
Hepatocellular Carcinoma. Front Med 8:762570. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​
1​0​.​3​3​8​9​/​f​m​e​d​.​2​0​2​1​.​7​6​2​5​7​0
Dumontet C, Jordan MA (2010) Microtubule-binding agents: a 
dynamic field of cancer therapeutics. Nat Rev Drug Discov 
9:790–803. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​n​r​d​3​2​5​3
Emens LA (2018) Breast Cancer Immunotherapy: Facts and Hopes. 
Clin Cancer Res 24:511–520. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​1​5​8​/​1​0​7​8​-​0​4​3​2​
.​C​C​R​-​1​6​-​3​0​0​1
Friedman J, Hastie T, Tibshirani R (2010) Regularization Paths for 
Generalized Linear Models via Coordinate Descent. J Stat Soft 
33. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​8​6​3​7​/​j​s​s​.​v​0​3​3​.​i​0​1
Fumagalli C, Barberis M (2021) Breast Cancer Heterogeneity. Diag­
nostics 11:1555. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​9​0​/​d​i​a​g​n​o​s​t​i​c​s​1​1​0​9​1​5​5​5
Gatica D, Lahiri V, Klionsky DJ (2018) Cargo recognition and degra­
dation by selective autophagy. Nat Cell Biol 20(3):233–242. ​h​t​t​p​
s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​s​4​1​5​5​6​-​0​1​8​-​0​0​3​7​-​z
Greenlee H, DuPont-Reyes MJ, Balneaves LG et al (2017) Clinical 
practice guidelines on the evidence‐based use of integrative ther­
apies during and after breast cancer treatment. CA Cancer J Clin 
67:194–232. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​2​2​/​c​a​a​c​.​2​1​3​9​7

Wherry EJ (2011) T cell exhaustion. Nat Immunol 12:492–499. ​h​t​t​p​s​:​
/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​n​i​.​2​0​3​5
Xia H, Green DR, Zou W (2021) Autophagy in tumour immunity and 
therapy. Nat Rev Cancer 21:281–297. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​s​4​
1​5​6​8​-​0​2​1​-​0​0​3​4​4​-​2
Xue X, Yang YA, Zhang A et al (2016) LncRNA HOTAIR enhances 
ER signaling and confers tamoxifen resistance in breast cancer. 
Oncogene 35:2746–2755. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​o​n​c​.​2​0​1​5​.​3​4​0
Yamamoto K, Venida A, Yano J et al (2020) Autophagy promotes 
immune evasion of pancreatic cancer by degrading MHC-I. 
Nature 581:100–105. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​s​4​1​5​8​6​-​0​2​0​-​2​2​2​9​-​5
Yang W, Soares J, Greninger P et al (2012) Genomics of Drug Sen­
sitivity in Cancer (GDSC): a resource for therapeutic biomarker 
discovery in cancer cells. Nucleic Acids Res 41:D955–D961. ​h​t​t​
p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​9​3​/​n​a​r​/​g​k​s​1​1​1​1
Yang L, Tian Y, Leong WS et al (2018) Efficient and tumor-specific 
knockdown of MTDH gene attenuates paclitaxel resistance of 
breast cancer cells both in vivo and in vitro. Breast Cancer Res 
20:113. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​1​8​6​/​s​1​3​0​5​8​-​0​1​8​-​1​0​4​2​-​7
Yi JS, Cox MA, Zajac AJ (2010) T-cell exhaustion: characteristics, 
causes and conversion. Immunology 129:474–481. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​
g​/​1​0​.​1​1​1​1​/​j​.​1​3​6​5​-​2​5​6​7​.​2​0​1​0​.​0​3​2​5​5​.​x
Yu B, Xing Z, Tian X, Feng R (2024a) A Prognostic Risk Signature 
of Two Autophagy-Related Genes for Predicting Triple-Negative 
Breast Cancer Outcomes. BCTT Volume 16:529–544. ​h​t​t​p​s​:​/​/​d​o​i​
.​o​r​g​/​1​0​.​2​1​4​7​/​B​C​T​T​.​S​4​7​5​0​0​7
Yu T, Rui L, Jiumei Z et al (2024b) Advances in the study of autophagy 
in breast cancer. Breast Cancer 31:195–204. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​
0​7​/​s​1​2​2​8​2​-​0​2​3​-​0​1​5​4​1​-​7
Zheng T, Li D, He Z et al (2018) Prognostic and clinicopathological 
significance of Beclin-1 in non-small-cell lung cancer: a meta-
analysis. OTT Volume 11:4167–4175. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​2​1​4​7​/​O​
T​T​.​S​1​6​4​9​8​7
Zhou Y, Zhou B, Pache L et al (2019) Metascape provides a biologist-
oriented resource for the analysis of systems-level datasets. Nat 
Commun 10:1523. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​s​4​1​4​6​7​-​0​1​9​-​0​9​2​3​4​-​6
Ritchie ME, Phipson B, Wu D et al (2015) limma powers differential 
expression analyses for RNA-sequencing and microarray studies. 
Nucleic Acids Res 43:e47–e47. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​9​3​/​n​a​r​/​g​k​v​0​
0​7
Samaddar JS, Gaddy VT, Duplantier J et al (2008) A role for mac­
roautophagy in protection against 4-hydroxytamoxifen–induced 
cell death and the development of antiestrogen resistance. Mol 
Cancer Ther 7:2977–2987. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​1​5​8​/​1​5​3​5​-​7​1​6​3​.​M​
C​T​-​0​8​-​0​4​4​7
Shenkier T (2004) Clinical practice guidelines for the care and treat­
ment of breast cancer: 15. Treatment for women with stage III or 
locally advanced breast cancer. Can Med Assoc J 170:983–994. ​h​
t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​5​0​3​/​c​m​a​j​.​1​0​3​0​9​4​4
Song Z, Wang Y, Li C et al (2015) Molecular Modification of Metad­
herin/MTDH Impacts the Sensitivity of Breast Cancer to Doxo­
rubicin. PLoS ONE 10:e0127599. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​3​7​1​/​j​o​u​r​n​a​
l​.​p​o​n​e​.​0​1​2​7​5​9​9
Sung H, Ferlay J, Siegel RL et al (2021) Global Cancer Statistics 2020: 
GLOBOCAN Estimates of Incidence and Mortality Worldwide 
for 36 Cancers in 185 Countries. CA Cancer J Clin 71:209–249. ​h​
t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​3​3​2​2​/​c​a​a​c​.​2​1​6​6​0
Szklarczyk D, Gable AL, Lyon D et al (2019) STRING v11: protein–
protein association networks with increased coverage, support­
ing functional discovery in genome-wide experimental datasets. 
Nucleic Acids Res 47:D607–D613. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​9​3​/​n​a​r​/​g​
k​y​1​1​3​1
The Cancer Genome Atlas Research Network, Weinstein JN, Collisson 
EA et al (2013) The Cancer Genome Atlas Pan-Cancer analysis 
project. Nat Genet 45:1113–1120. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​n​g​.​2​7​
6​4
Tran WT, Childs C, Probst H et al (2018) Imaging Biomarkers for 
Precision Medicine in Locally Advanced Breast Cancer. J Med 
Imaging Radiation Sci 49:342–351. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​1​6​/​j​.​j​m​
i​r​.​2​0​1​7​.​0​9​.​0​0​6
Triulzi T, Regondi V, De Cecco L et al (2018) Early immune modu­
lation by single-agent trastuzumab as a marker of trastuzumab 
benefit. Br J Cancer 119:1487–1494. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​.​1​0​3​8​/​s​4​1​
4​1​6​-​0​1​8​-​0​3​1​8​-​0
Wang H, Sun P, Yuan X et al (2025) Autophagy in tumor immune 
escape and immunotherapy. Mol Cancer 24:85. ​h​t​t​p​s​:​/​/​d​o​i​.​o​r​g​/​1​0​
.​1​1​8​6​/​s​1​2​9​4​3​-​0​2​5​-​0​2​2​7​7​-​y
