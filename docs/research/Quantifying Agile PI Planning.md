

# **The Quantified Value Framework (QVF): A Prescriptive Guide to Objective Prioritization in Enterprise Agile**

## **Introduction**

This report addresses the pervasive challenge of subjective, "feeling-based" prioritization within scaled agile frameworks like SAFe. It presents the Quantified Value Framework (QVF), a definitive, data-driven methodology designed to replace intuition with a quantifiable, explainable, and automated system. The QVF ensures that strategic alignment and true value delivery are the primary drivers of all planning and execution decisions.

The core problem stems from well-intentioned but fundamentally flawed agile practices. Teams are asked to assign a "business value" number at the start of a Program Increment (PI), but this score is often a proxy for intuition rather than a product of rigorous analysis.1 This inaccuracy leads to friction, stress from unplanned work, and significant challenges when applying agile principles to non-development functions like compliance or process operations. Industry critiques echo this sentiment, noting that frameworks like SAFe can devolve into top-down bureaucracies where the connection to true business agility is lost.2 The long planning horizons can reduce adaptability, making a robust, objective prioritization system paramount to success.1

The Quantified Value Framework (QVF) is a hybrid model designed to solve this problem. It integrates the strategic discipline of Six Sigma, the process-centric view of Lean Value Stream Management, and the mathematical rigor of the Analytic Hierarchy Process (AHP).6 This report provides a complete, prescriptive guide for implementing the QVF, including detailed instructions for automation within the Azure DevOps (ADO) environment.

## **Section 1: Deconstructing Value \- The Failures of Conventional Agile Prioritization**

To establish the need for a new paradigm, it is essential to first deconstruct the conventional prioritization methods used in agile environments and expose their inherent inadequacies. These methods, while popular, fail to provide the objective, quantifiable foundation required for high-stakes enterprise decision-making.

### **1.1 The Illusion of "Business Value" in PI Planning**

The standard SAFe practice of assigning a "Business Value" (BV) on a 1-10 scale to PI Objectives is intended to foster engagement and secure buy-in from business stakeholders.1 While this achieves a level of alignment, the process is fundamentally flawed. The BV score is a proxy for importance, but it lacks a defined, consistent model for its calculation. It is, as the query suggests, a "feeling" converted to a number.

This subjectivity makes the process highly susceptible to several distorting influences. It can be dominated by the "HiPPO" (Highest Paid Person's Opinion), where the executive with the most authority dictates priorities regardless of data. It also encourages political horse-trading between departments, where value scores are negotiated to serve parochial interests rather than enterprise goals.10 This inconsistency is magnified when different Agile Release Trains (ARTs) or teams apply their own unique interpretations of what a "10" or a "5" represents. This ultimately leads organizations into the "build trap," where teams become highly efficient at delivering features (outputs) that have high but arbitrary BV scores, without a clear, quantifiable link to actual business or customer results (outcomes).2

### **1.2 The Mathematical Fallacy of Weighted Shortest Job First (WSJF)**

SAFe prescribes Weighted Shortest Job First (WSJF) as its primary method for sequencing Features and Epics, using the formula WSJF \= Cost of Delay (CoD) / Job Size.11 The Cost of Delay is calculated by summing three components: User-Business Value, Time Criticality, and Risk Reduction/Opportunity Enablement.12 This approach appears more sophisticated, but it merely disaggregates one subjective estimate into three smaller subjective estimates. These components are often rated on the same flawed Fibonacci-style relative scale used for effort estimation, which does not remove subjectivity but only obscures it behind a more complex formula.10

The true deficiency of WSJF, however, lies in its mathematics. The use of division is its Achilles' heel.13 In any estimation, the estimated value can be represented as the actual value plus an error term. In additive systems, such as summing story points for a release forecast, random estimation errors (some over, some under) tend to cancel each other out over a large sample of items. In divisive systems like WSJF, these errors compound exponentially.13

This compounding effect is magnified by the non-linear Fibonacci scale (1, 2, 3, 5, 8, 13...). An estimate that is off by just a single notch on this scale—for instance, estimating a size of 8 when the actual size is 5—can introduce a 60% error from the outset.13 When a Cost of Delay estimate with a large positive error is divided by a Job Size estimate with a large negative error, the resulting WSJF score can be orders of magnitude wrong. This creates a false sense of scientific precision that is dangerously misleading.

Consider a scenario with four features where estimates for value and size are imperfect 13:

| Item | Est. Value | Est. Size | Est. WSJF | Act. Value | Act. Size | Act. WSJF |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| A | 8 | 5 | **1.6** | 5 | 5 | 1.00 |
| B | 8 | 8 | **1.0** | 3 | 20 | 0.15 |
| C | 3 | 5 | **0.6** | 8 | 2 | 4.00 |
| D | 5 | 13 | **0.4** | 13 | 2 | 6.50 |

Based on the estimated WSJF, the prioritized order would be A, B, C, D. However, the actual optimal economic sequence, based on the real values, is D, C, A, B—the complete inverse. This demonstrates that WSJF is not just inaccurate; it can actively guide an organization to make the worst possible prioritization decisions, all while providing the illusion of an objective, economic basis.13

### **1.3 Limitations of Other Common Prioritization Techniques**

Other popular agile prioritization methods suffer from similar, if less mathematically insidious, flaws.

* **MoSCoW (Must, Should, Could, Won't):** This method categorizes features based on necessity. However, it is inherently subjective. What one stakeholder deems a "Must-have" another may see as a "Should-have," leading to protracted debates that lack a data-driven resolution mechanism. It becomes a battle of wills rather than a strategic exercise.14  
* **RICE (Reach, Impact, Confidence, Effort):** While more structured than MoSCoW, the RICE model still relies on subjective inputs. The "Impact" and "Confidence" scores are often "gut feelings" assigned by a product manager, lacking a defensible quantitative basis and varying wildly between individuals.14  
* **Value vs. Effort Matrix:** This 2x2 matrix is useful for quickly identifying "low-hanging fruit" (high value, low effort). However, it is a blunt instrument, not a strategic tool. It oversimplifies complex value propositions and ignores critical factors such as strategic alignment, risk mitigation, and inter-item dependencies, making it unsuitable for comprehensive portfolio management.16

The systemic failure across these conventional frameworks is their reliance on non-quantified, subjective inputs. They are all susceptible to the "Garbage In, Garbage Out" principle. This failure is a major contributor to the documented problems with scaled agile implementations, including a focus on outputs over outcomes, organizational friction, and a strategic disconnect between development activities and business goals.2 A new approach is needed—one that builds a definition of value from the ground up using objective data and structured, consistent judgment.

## **Section 2: A New Foundation \- Integrating Principles from Six Sigma, Lean, and Decision Science**

The Quantified Value Framework is built upon a synthesis of mature, proven methodologies from outside the mainstream agile canon. By integrating the strategic discipline of Six Sigma, the process-centric view of Lean, and the mathematical rigor of Decision Science, the QVF creates a robust and defensible foundation for prioritization.

### **2.1 Strategic Alignment and Data-Driven Selection: Lessons from Six Sigma**

Six Sigma is a discipline focused on using data and statistical analysis to measure and improve operational performance and quality.6 Its highly structured approach to project selection provides the first pillar of the QVF: ensuring that work is strategically aligned and financially sound.

* **Principle 1: Strategic Goal Alignment.** A core tenet of Six Sigma is that a project is only worth doing if it is explicitly linked to the organization's overarching strategic goals and has clear, unwavering management support.6 The QVF adopts this principle by mandating that all prioritization criteria must cascade directly from the highest-level corporate objectives, such as Objectives and Key Results (OKRs) or Strategic Themes.  
* **Principle 2: Quantifiable Impact.** Six Sigma project selection is based on objective, quantifiable data, not relative estimates.6 A candidate project must demonstrate a clear, measurable gap between current and desired performance and project a significant financial impact.18 This principle directly counters the "relative value" approach common in agile and forces a conversation grounded in concrete numbers.  
* **Principle 3: The Voice of the Customer (VoC).** Six Sigma emphasizes sourcing improvement opportunities from both internal and external data streams. This includes formal VoC analysis, customer complaint logs, market surveys, and competitive analysis.6 This provides an objective, data-rich source for defining value criteria related to customer satisfaction and market demand.

### **2.2 Identifying True Value: Applying Lean's Value Stream and Waste Reduction Principles**

Value Stream Mapping (VSM) is a cornerstone Lean technique used to analyze and improve the end-to-end flow of value delivery to a customer.7 It provides the second pillar of the QVF: the ability to quantify the value of internal process and operational improvements, a critical need for the non-development teams mentioned in the query.

* **Principle 1: Value is Defined by the Customer.** In Lean philosophy, any activity, process, or feature that does not add value from the customer's perspective is classified as waste.21 The QVF incorporates this by including criteria that explicitly measure the reduction of identifiable waste, such as rework, delays, handoffs, and over-processing.20  
* **Principle 2: Quantifying Process Efficiency.** VSM utilizes flow metrics like cycle time, lead time, wait time, and process time to quantify the health of a value stream.20 An Epic designed to improve one of these metrics—for example, automating a manual compliance check to reduce its cycle time from weeks to hours—has a tangible, quantifiable operational value. This is essential for comparing development work against process improvement work on a level playing field.  
* **Principle 3: System-Level Optimization.** VSM provides a holistic view of the entire system, preventing local optimizations by one team that might inadvertently create bottlenecks or problems for another.21 This reinforces the need for a comprehensive prioritization model that considers cross-team dependencies and system-wide impact, a common pain point in SAFe.2

### **2.3 The Decisive Component: The Analytic Hierarchy Process (AHP)**

While Six Sigma and Lean provide the sources of value, they do not offer a mechanism to weigh competing value types against each other. Is a $1M revenue-generating Epic more important than one that mitigates a critical security risk? To solve this, the QVF employs the Analytic Hierarchy Process (AHP) as its decision-making engine. AHP is a multi-criteria decision-making (MCDM) framework designed specifically for complex problems involving both quantitative and qualitative factors.8 Notably, independent research has identified AHP as one of the few "suitable" methods for large-scale project portfolio prioritization in major organizations.25

* **Feature 1: Hierarchical Decomposition.** AHP structures a complex decision into a simple hierarchy: a Goal at the top, Criteria in the middle, and Alternatives at the bottom.26 This structure maps perfectly to the strategic planning hierarchy in agile: Goal (e.g., Maximize PI Value), Criteria (the QVF value drivers), and Alternatives (the Epics or PI Objectives to be prioritized).  
* **Feature 2: Pairwise Comparisons.** AHP's most powerful feature is its method for weighting criteria. Instead of asking stakeholders to assign abstract percentage weights, AHP uses a series of simple, relative judgments based on Saaty's 1-9 scale.26 Stakeholders are asked, "Is Criterion A more important than Criterion B, and by how much?" Research shows that humans are far more reliable at making these relative judgments than assigning absolute weights.25 This process fosters collaboration and forces a structured conversation about strategic trade-offs.29  
* **Feature 3: The Consistency Ratio (The "Bulletproof" Mechanism).** This is the cornerstone of the QVF's defensibility and objectivity. After the pairwise comparisons are complete, AHP mathematically calculates a Consistency Ratio (CR) that measures the logical consistency of the decision-maker's judgments.30 For example, if a stakeholder states that A is more important than B, and B is more important than C, but then states that C is more important than A, their judgments are inconsistent. AHP quantifies this inconsistency. If the CR exceeds a threshold of 0.10, the judgments are deemed statistically unreliable and must be revisited.32 This provides an objective, mathematical basis to challenge and refine stakeholder input, effectively removing "feeling" from the weighting process and ensuring the model's integrity.

By synthesizing these three disciplines, the QVF creates a comprehensive system. Six Sigma provides the "what" to prioritize (strategic, financial goals). Lean provides the lens to quantify the "how" (the value of improving the process itself). AHP provides the mathematically sound engine to weigh these disparate value drivers and produce a single, rationalized priority score.

## **Section 3: The Quantified Value Framework (QVF) \- A Multi-Criteria Decision Model**

This section presents the detailed architecture of the QVF, translating the foundational principles into a concrete, structured model that can be implemented within an organization.

### **3.1 The AHP-Powered Prioritization Engine**

The core of the QVF is an engine driven by the Analytic Hierarchy Process. The application of AHP within the QVF follows a structured, multi-step process:

1. **Define the Hierarchy:** The decision is structured into a clear hierarchy. The top-level **Goal** is established (e.g., "Maximize Value Delivery in PI-X"). The next level consists of the **Criteria** that define value, as detailed in the QVF Criteria Matrix. The bottom level contains the **Alternatives**—the Epics, PI Objectives, or other initiatives being evaluated.34  
2. **Conduct Pairwise Comparisons of Criteria:** Key stakeholders, such as Business Owners, Release Train Engineers (RTEs), and Enterprise Architects, collaboratively participate in a pairwise comparison exercise. For each pair of criteria, they judge which is more important and by how much, using Saaty's 1-9 scale. This structured dialogue is crucial for building consensus and ensuring all perspectives are considered.29  
3. **Calculate Priority Weights:** Using the inputs from the pairwise comparisons, the AHP engine employs linear algebra (specifically, eigenvector calculation) to derive a normalized priority weight for each criterion. This weight represents its relative importance in achieving the overall goal.26  
4. **Score Alternatives against each Criterion:** Each alternative (Epic) is then scored against each individual criterion. This is not a subjective guess. Instead, the Epic's attributes are mapped to a predefined, objective scoring scale. For example, if an Epic's NPV is calculated to be $500,000, it might receive a score of "4" on the 1-5 scale defined for the NPV criterion.25  
5. **Calculate Final Scores:** A final, weighted score is calculated for each Epic using a weighted sum formula: FinalScore=∑(CriterionWeight×Epic′sScoreCriterion​). This yields a single, normalized priority score for every alternative.24  
6. **Check Consistency:** The Consistency Ratio (CR) is calculated for the criteria comparison matrix. If the CR is greater than 0.10, it signals that the stakeholder judgments are logically inconsistent. The process is halted, and the stakeholders must revisit their comparisons to resolve the inconsistencies before the final scores are accepted as valid.30

### **3.2 The QVF Hierarchy: Goals, Criteria, and Work Items**

The QVF model maps directly onto the hierarchical structure of work items commonly used in Azure DevOps and other agile tools. This creates a clear line of sight from strategic goals to execution.

* **Level 0: Goal** (The overall objective for the planning period, e.g., "Maximize Q3 2025 Business Impact")  
* **Level 1: Criteria Categories** (The main pillars of value, e.g., Financial Impact, Strategic Alignment)  
* **Level 2: Sub-Criteria** (The specific, measurable metrics within each category, e.g., NPV, Cycle Time Reduction)  
* **Level 3: Alternatives** (The Epics or PI Objectives being evaluated and scored)  
* **Level 4 & Below:** Features, User Stories, Tasks (Work items whose value is derived from their parent, not calculated directly via AHP)

### **3.3 The QVF Criteria Matrix**

The heart of the QVF is its criteria matrix. This matrix makes the abstract concept of "value" concrete, transparent, and measurable. It serves as a starting point that an organization must collaboratively define and agree upon. The act of creating this matrix is itself a valuable strategic alignment exercise.

**Table 1: The QVF Criteria Matrix (Example)**

| Criterion Category | Sub-Criterion | Definition | Unit of Measure | Data Source / Measurement Method | Scoring Scale (1-5 Example) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Strategic Alignment** | Alignment with OKR 1: "Increase Market Share" | Degree to which the epic directly contributes to the stated objective of increasing market share. | Qualitative Score | Product Strategy Document, Executive Sponsor Input | 1: No impact \-\> 5: Critical enabler |
|  | Alignment with OKR 2: "Improve Customer Retention" | Degree to which the epic directly contributes to improving customer retention metrics. | % point increase | Analytics Team, Customer Success Platform Data | 1: \<0.1% \-\> 5: \>2% |
| **Financial Impact** | Net Present Value (NPV) | The total present value of future cash flows minus the initial investment. | USD ($) | Finance Department's official Cost-Benefit Analysis (CBA) model.37 | 1: \<$50k \-\> 5: \>$1M |
|  | Cost of Poor Quality (COPQ) Reduction | Estimated reduction in costs associated with rework, scrap, and defects. | USD ($) | From Six Sigma / Process Improvement analysis.18 | 1: \<$10k \-\> 5: \>$250k |
| **Risk & Compliance** | Mitigate Security Risk | Reduces the likelihood or impact of a known security vulnerability, measured by risk score. | Risk Score (1-25) | Security Team's Risk Register | 1: Low risk \-\> 5: Critical risk |
|  | Meet Regulatory Deadline | Is this work required to meet a fixed, external regulatory or legal deadline? | Binary (Yes/No) | Legal/Compliance Department | 1: No \-\> 5: Yes |
| **Operational Improvement** | Process Cycle Time Reduction | The reduction in total time from when work starts on an item until it is delivered. | Days | Value Stream Mapping (VSM) analysis.7 | 1: \<1 day \-\> 5: \>15 days |
|  | Reduce Manual Toil | The percentage of manual effort automated by the initiative. | % of FTE hours/wk | VSM / Process Analysis | 1: \<5% \-\> 5: \>50% |
| **Customer Value** | Improve Customer Satisfaction (CSAT) | The expected increase in the customer satisfaction score for the affected product/service. | CSAT points | Voice of the Customer (VoC) data, Surveys.6 | 1: \<0.5 pts \-\> 5: \>3 pts |
|  | Enable New Customer Segments | Does this work open up a new, previously unreachable market or customer segment? | Binary (Yes/No) | Market Research, Business Case | 1: No \-\> 5: Yes |

This matrix forces the organization to move beyond vague notions of value. For each way value can be generated, it demands answers to four critical questions: What do we mean? How do we measure it? Where does the data come from? And how do we score it? This structure provides the objective inputs required by the AHP engine and makes the entire prioritization process transparent, auditable, and defensible.

## **Section 4: The QVF Scoring Engine \- A Cascading Hierarchy of Value**

A common anti-pattern in agile is attempting to assign business value to every individual user story. This is inefficient and often meaningless, as a single story rarely delivers standalone value. The QVF corrects this by calculating value at the highest strategic level (Epics) and cascading it down through the work item hierarchy. This ensures that all work remains anchored to the strategic intent.

### **4.1 Level 1: Epic and PI Objective Scoring**

The primary calculation occurs at the Epic or PI Objective level. These high-level work items are the "Alternatives" evaluated using the full AHP process described in Section 3\. The output for each Epic is a final, normalized priority score (e.g., a decimal value between 0.0 and 1.0) and a corresponding rank against all other Epics. This score, validated by the Consistency Ratio, represents the Epic's total intrinsic value to the organization for the given planning horizon.

### **4.2 Level 2: Deriving Feature Scores**

Features are children of Epics. Their value is not calculated independently but is derived as a portion of their parent Epic's total value. This allocation is based on the relative effort required for each Feature. While any effort metric can be used, Story Points are a common choice.

The formula for allocating value is:

FeatureScore=(ParentEpicAHPScore)×∑(Size of all child Features)FeatureSize​  
This approach ensures that the sum of the value of the parts (Features) equals the value of the whole (Epic). It correctly reflects that a small, simple Feature contributing to a high-value Epic is more important than a large, complex Feature contributing to a low-value Epic. This incentivizes breaking down work into smaller pieces without "losing" value in the prioritization model.

### **4.3 Level 3 & 4: User Story and Task Prioritization**

The same allocation logic cascades down the hierarchy. A User Story's value is derived from its parent Feature's calculated score, again allocated based on its relative size compared to its sibling stories.

The formula is:

UserStoryScore=(ParentFeatureScore)×∑(Size of all child User Stories)UserStorySize​  
Tasks, which are the children of User Stories, are typically not scored for value. They represent the specific work required to deliver the story, and their priority is implicitly dictated by the priority of their parent story. The team sequences tasks based on technical dependencies and workflow optimization.

### **4.4 Incorporating Dynamic Factors and Overlays**

The cascaded QVF score represents the intrinsic, strategic value of a work item. For practical PI planning, this base score should be augmented with dynamic, tactical factors to create a final, executable sequence.

* **Dependency Overlay:** Cross-team dependencies are a significant source of friction and delay in SAFe.2 A dependency analysis must be performed. Work items that are identified as blockers for multiple other high-value items should have their priority temporarily elevated. This can be implemented as a simple flag or a priority multiplier in reporting to ensure they are addressed early in the PI.  
* **Implementation Risk Overlay:** The QVF model already incorporates strategic and business risk as a criterion. However, implementation risk—such as high technical uncertainty, reliance on a new technology, or team skill gaps—can be used as a secondary sorting factor. For two Features with very similar QVF scores, the team and product manager might choose to sequence the lower-risk item first to secure early, predictable value delivery and build momentum.

The final rank for PI Planning is therefore a function of the base QVF score, adjusted for these critical tactical overlays. This approach changes the nature of backlog refinement. The conversation shifts from "How much value does this story have?" to "Is this story the most efficient way to contribute to delivering its parent Feature's allocated value?" It focuses teams on the efficient delivery of strategically important work.

## **Section 5: Prescriptive Implementation Guide for Azure DevOps**

This section provides a practical, step-by-step manual for implementing the Quantified Value Framework within an Azure DevOps (ADO) environment. The implementation is divided into three phases: process customization, automation engine construction, and reporting visualization.

### **5.1 Phase 1: Process and Work Item Customization**

ADO's default system processes (Agile, Scrum, CMMI) are locked and cannot be modified. Therefore, the first step is to create an **Inherited Process**. This creates a customizable copy of a system process that can be tailored to support the QVF.38

Once the inherited process is created, custom fields must be added to the relevant Work Item Types (WITs), such as Epic, Feature, and User Story, to store the QVF data.40 The following table serves as the definitive schema for this customization, providing the necessary details for each field. This structured approach is critical for ensuring the subsequent automation phase functions correctly.

**Table 2: QVF-to-ADO Field Mapping**

| QVF Metric Name | ADO Field Label | ADO Reference Name | ADO Data Type | Work Item Type(s) | Purpose |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Input Criteria Scores** |  |  |  |  |  |
| NPV Score | QVF \- NPV Score | Custom.QVFNPVScore | Integer | Epic, PI Objective | Stores the 1-5 score for the NPV criterion. |
| OKR-1 Alignment Score | QVF \- OKR1 Align Score | Custom.QVFOKR1AlignScore | Integer | Epic, PI Objective | Stores the 1-5 score for alignment with the first OKR. |
| Cycle Time Reduction Score | QVF \- Cycle Time Score | Custom.QVFCycleTimeScore | Integer | Epic, PI Objective | Stores the 1-5 score for the Cycle Time Reduction criterion. |
| *... (etc. for all sub-criteria in Table 1\)* | *...* | *...* | *...* | *...* | *...* |
| **AHP Calculation Fields** |  |  |  |  |  |
| AHP Criteria Weights | QVF \- AHP Criteria Weights | Custom.QVFAHPCriteriaWeights | PlainText | (Stored externally or in a single configuration WIT) | JSON string storing the calculated weights for all criteria. |
| AHP Consistency Ratio | QVF \- AHP Consistency Ratio | Custom.QVFAHPConsistencyRatio | Decimal | (Stored externally or in a single configuration WIT) | Stores the calculated CR. If \>0.1, indicates an input problem. |
| **Output Scores** |  |  |  |  |  |
| AHP Final Score | QVF \- AHP Final Score | Custom.QVFAHPFinalScore | Decimal | Epic, PI Objective | The final, normalized priority score from the AHP calculation. |
| Cascaded Value Score | QVF \- Cascaded Value | Custom.QVFCascadedValue | Decimal | Feature, User Story | The value score allocated from the parent work item. |
| Final PI Rank | QVF \- Final PI Rank | Custom.QVFPIRank | Integer | Epic, Feature | The final sorted rank for PI Planning, after overlays. |

### **5.2 Phase 2: Building the Automation Engine**

ADO does not natively support complex calculations like AHP or even simple field roll-ups without marketplace extensions.42 An external automation engine is therefore a mandatory component of the QVF implementation.

#### **Option A: The Power Automate Approach (Lower Code)**

For organizations preferring a low-code solution, Power Automate can orchestrate the QVF calculations.44

* **Trigger:** The flow can be initiated on a schedule (e.g., nightly) or triggered manually by a user.  
* **High-Level Steps:**  
  1. **Get Work Items:** Use the ADO connector's "Get query results" action with a Work Item Query Language (WIQL) query to pull all candidate Epics for the upcoming PI.  
  2. **Read Inputs:** Loop through each Epic and use the "Get work item details" action to read the values from all the custom Custom.QVF...Score input fields.  
  3. **Call Azure Function for AHP:** Power Automate is not designed for the matrix algebra required by AHP. The most effective pattern is to package the AHP calculation logic into a simple, HTTP-triggered Azure Function. The Power Automate flow sends the input scores and criteria weights to the function via an HTTP action. The function performs the AHP calculation (including the consistency check) and returns a JSON object with the final scores.  
  4. **Update Work Items:** Use the "Update a work item" action to write the calculated Custom.QVFAHPFinalScore back to the corresponding Epic work item in ADO.46  
  5. **Cascade Scores:** Implement a subsequent loop. For each scored Epic, get its child Features. Calculate the Custom.QVFCascadedValue for each Feature based on the allocation formula and update the Feature work items. This process is repeated for User Stories.

#### **Option B: The Azure Functions & REST API Approach (Higher Control)**

For a more robust, scalable, and customizable solution, a dedicated Azure Function can be built to house the entire QVF engine, interacting directly with the ADO REST API.

* **Trigger:** The Azure Function can be triggered on a timer, by an HTTP request (e.g., from a logic app or custom button), or via an ADO Service Hook that fires when a relevant work item is updated.  
* **Logic and API Calls:** The function's code would perform all necessary operations using the ADO REST API.48  
  * **Query:** Use the Wiql \- Query By Wiql endpoint to find the set of work items to be processed.50  
  * **Read:** Use the Work Items \- Get Work Item endpoint to retrieve the full details of each work item, including the custom field values.51  
  * **Calculate:** The core AHP logic and the value cascade calculations are implemented directly in the function's code (e.g., using Python with NumPy or C\# with a math library).  
  * **Write:** Use the Work Items \- Update endpoint with a PATCH method and a Content-Type of application/json-patch+json to write the calculated scores back to the custom fields on the work items.53

### **5.3 Phase 3: Reporting and Visualization with Power BI**

The final phase is to make the results of the QVF transparent and actionable for all stakeholders through a comprehensive Power BI dashboard.

* **Data Connection:** Connect Power BI to the Azure DevOps Analytics service using the recommended OData method. This approach is superior to the legacy Data Connector as it fully supports custom fields and allows for powerful server-side filtering and aggregation of data, which is essential for performance with large datasets.55  
* **OData Queries:** Construct OData queries to pull the necessary work item data (Epics, Features, Stories) into Power BI. The queries must be written to include all the new custom Custom.QVF... fields created in Phase 1\.  
* **Dashboard Visuals:** The dashboard should be designed to provide clarity and facilitate decision-making. Key visuals include:  
  * **Prioritized Backlog:** A table or matrix visual showing a ranked list of Epics and Features, sorted by the QVF \- Final PI Rank field.  
  * **Explainable Score Breakdown:** A stacked bar chart for each Epic, showing its total QVF \- AHP Final Score. The segments of each bar should represent the weighted contribution from each criterion category (e.g., Financial, Strategic, Risk). This visual is critical for explaining *why* an Epic received its score.  
  * **Consistency Check Gauge:** A card or gauge visual that displays the QVF \- AHP Consistency Ratio. The visual should be configured to turn red if the value exceeds the 0.10 threshold, providing an immediate, high-visibility warning of inconsistent inputs.  
  * **Slicers and Filters:** Interactive slicers that allow stakeholders to filter the prioritized backlog by Team, Strategic Theme, PI, or any other relevant field.

## **Conclusion: Cultivating a Culture of Objective, Data-Driven Decision-Making**

The Quantified Value Framework (QVF) directly addresses the core challenges of subjective, feeling-based prioritization in agile environments. By systematically integrating principles from Six Sigma, Lean, and the Analytic Hierarchy Process, it delivers a solution characterized by objectivity, transparency, and defensibility.

* **Objectivity:** The QVF replaces arbitrary "business value" scores with a structured model where value is derived from measurable, data-driven criteria tied to strategic goals, financial impact, and operational improvement.6  
* **Transparency and Explainability:** The framework's logic is clear and auditable. The Power BI dashboards provide stakeholders with a complete view of not only *what* is prioritized but *why*, showing the specific contribution of each value driver to the final score.  
* **Defensibility:** The use of AHP's Consistency Ratio provides a mathematical, "bulletproof" mechanism to ensure that stakeholder judgments, which form the weights of the model, are logical and consistent. This removes the "loudest voice" from the room and grounds the conversation in rational trade-offs.30  
* **Strategic Alignment:** The entire framework is anchored to the organization's highest-level objectives, ensuring a clear line of sight from top-level strategy to the daily work of development and operations teams.

Adopting the QVF is more than a process or tool implementation; it is a catalyst for a significant cultural shift. It moves the act of prioritization from a confrontational debate based on opinion to a structured, collaborative analysis based on shared data and logic. This transformation reduces the friction and stress associated with PI planning and builds deep, lasting trust in the process. While this represents a significant investment in process maturity, the QVF provides the necessary mechanism to escape the "build trap" 2 and ensure that an organization's most valuable resources are perpetually focused on its most important initiatives—as defined by data, not by feelings.

#### **Works cited**

1. Pros and Cons of Scaled Agile Framework (SAFe) | by Ramki R ..., accessed on July 31, 2025, [https://medium.com/@cinemaparadiso/pros-and-cons-of-scaled-agile-framework-safe-cc142f0c74cf](https://medium.com/@cinemaparadiso/pros-and-cons-of-scaled-agile-framework-safe-cc142f0c74cf)  
2. Three reasons why Equal Experts doesn't recommend the SAFe framework, accessed on July 31, 2025, [https://www.equalexperts.com/blog/our-thinking/problems-with-safe-framework/](https://www.equalexperts.com/blog/our-thinking/problems-with-safe-framework/)  
3. 5 Disadvantages of Scaled Agile Framework (SAFe) | Insights Spotter, accessed on July 31, 2025, [https://insightspotter.com/5-disadvantages-of-scaled-agile-framework-safe/](https://insightspotter.com/5-disadvantages-of-scaled-agile-framework-safe/)  
4. Pros and Cons of Scaled Agile Framework | SAFe Advantages and Disadvantages, accessed on July 31, 2025, [https://premieragile.com/advantages-and-disadvantages-of-scaled-agile-framework/](https://premieragile.com/advantages-and-disadvantages-of-scaled-agile-framework/)  
5. I just entered a week of what is called PI planning in SAFe. What the fuck is go... | Hacker News, accessed on July 31, 2025, [https://news.ycombinator.com/item?id=31587201](https://news.ycombinator.com/item?id=31587201)  
6. Selecting Six Sigma Projects \- Six Sigma Study Guide, accessed on July 31, 2025, [https://sixsigmastudyguide.com/selecting-six-sigma-projects/](https://sixsigmastudyguide.com/selecting-six-sigma-projects/)  
7. A Step-By-Step Guide to Value Stream Management \- Lucid Software, accessed on July 31, 2025, [https://lucid.co/blog/value-stream-management](https://lucid.co/blog/value-stream-management)  
8. Prioritizing project risks using AHP \- Project Management Institute, accessed on July 31, 2025, [https://www.pmi.org/learning/library/project-decision-making-tool-7292](https://www.pmi.org/learning/library/project-decision-making-tool-7292)  
9. Top 3 challenges of agile PI Planning (and how to overcome them), accessed on July 31, 2025, [https://www.easyagile.com/blog/top-3-challenges-agile-pi-planning-jira](https://www.easyagile.com/blog/top-3-challenges-agile-pi-planning-jira)  
10. SAFe and Weighted Shortest Job First (WSJF) | Black Swan Farming, accessed on July 31, 2025, [https://blackswanfarming.com/safe-and-weighted-shortest-job-first-wsjf/](https://blackswanfarming.com/safe-and-weighted-shortest-job-first-wsjf/)  
11. What is WSJF – Weighted Shortest Job First SAFe? \- Scrum-Master·Org, accessed on July 31, 2025, [https://scrum-master.org/en/what-is-wsjf-weighted-shortest-job-first-safe/](https://scrum-master.org/en/what-is-wsjf-weighted-shortest-job-first-safe/)  
12. Weighted Shortest Job First (WSJF): What It Is & How to Use It \- Fibery, accessed on July 31, 2025, [https://fibery.io/blog/product-management/wsjf/](https://fibery.io/blog/product-management/wsjf/)  
13. Why WSJF is Nonsense \- Fail Fast, Move On, accessed on July 31, 2025, [https://failfastmoveon.blogspot.com/2021/03/why-wsjf-is-nonsense.html](https://failfastmoveon.blogspot.com/2021/03/why-wsjf-is-nonsense.html)  
14. 9 Agile Prioritization Techniques to Improve Workflows \- Axify, accessed on July 31, 2025, [https://axify.io/blog/agile-prioritization-techniques](https://axify.io/blog/agile-prioritization-techniques)  
15. Mastering Agile prioritization techniques: 4 simple yet powerful tools for Scrum excellence, accessed on July 31, 2025, [https://www.rst.software/blog/mastering-agile-prioritization-techniques-4-simple-yet-powerful-tools-for-scrum-excellence](https://www.rst.software/blog/mastering-agile-prioritization-techniques-4-simple-yet-powerful-tools-for-scrum-excellence)  
16. 10 Best Prioritization Techniques for Agile in 2025 \- EARLY's time-tracking, accessed on July 31, 2025, [https://early.app/blog/best-prioritization-techniques/](https://early.app/blog/best-prioritization-techniques/)  
17. What Is an Agile Prioritization Matrix? \- Product School, accessed on July 31, 2025, [https://productschool.com/blog/product-fundamentals/agile-prioritization-matrix](https://productschool.com/blog/product-fundamentals/agile-prioritization-matrix)  
18. The Two Key Criteria for Successful Six Sigma Project Selection \- Innocentrix, accessed on July 31, 2025, [https://innocentrix.com/files/wpsuccessfulsixsigmaprojectselection.pdf](https://innocentrix.com/files/wpsuccessfulsixsigmaprojectselection.pdf)  
19. A Guide to Strategic Project Selection in Lean Six Sigma \- GoLeanSixSigma.com (GLSS), accessed on July 31, 2025, [https://goleansixsigma.com/project-selection/](https://goleansixsigma.com/project-selection/)  
20. Value Stream Mapping | Atlassian, accessed on July 31, 2025, [https://www.atlassian.com/continuous-delivery/principles/value-stream-mapping](https://www.atlassian.com/continuous-delivery/principles/value-stream-mapping)  
21. What Is Value Stream Mapping? \- Planview, accessed on July 31, 2025, [https://www.planview.com/resources/guide/lean-principles-101/what-is-value-stream-mapping/](https://www.planview.com/resources/guide/lean-principles-101/what-is-value-stream-mapping/)  
22. Value Stream Analysis: The key to leaner operations \- Kaizen Institute, accessed on July 31, 2025, [https://kaizen.com/insights/value-stream-analysis-leaner-operations/](https://kaizen.com/insights/value-stream-analysis-leaner-operations/)  
23. Our PI planning used to be a mess—here's what helped us fix it : r/agile \- Reddit, accessed on July 31, 2025, [https://www.reddit.com/r/agile/comments/1iiayqv/our\_pi\_planning\_used\_to\_be\_a\_messheres\_what/](https://www.reddit.com/r/agile/comments/1iiayqv/our_pi_planning_used_to_be_a_messheres_what/)  
24. Make Effective Decisions. Comprehensive Guide to Analytic Hierarchy Process (AHP), accessed on July 31, 2025, [https://www.6sigma.us/six-sigma-in-focus/analytic-hierarchy-process-ahp/](https://www.6sigma.us/six-sigma-in-focus/analytic-hierarchy-process-ahp/)  
25. Why AHP works for Prioritization \- Strategic Decision Making | TransparentChoice Blog, accessed on July 31, 2025, [https://blog.transparentchoice.com/why-ahp-works-for-prioritization](https://blog.transparentchoice.com/why-ahp-works-for-prioritization)  
26. What is the Analytical Hierarchy Process? And How Does it Work? \- OnlinePMCourses, accessed on July 31, 2025, [https://onlinepmcourses.com/what-is-the-analytical-hierarchy-process-and-how-does-it-work/](https://onlinepmcourses.com/what-is-the-analytical-hierarchy-process-and-how-does-it-work/)  
27. Analytic hierarchy process \- Wikipedia, accessed on July 31, 2025, [https://en.wikipedia.org/wiki/Analytic\_hierarchy\_process](https://en.wikipedia.org/wiki/Analytic_hierarchy_process)  
28. What is the Analytic Hierarchy Process (AHP)? \- 1000minds, accessed on July 31, 2025, [https://www.1000minds.com/decision-making/analytic-hierarchy-process-ahp](https://www.1000minds.com/decision-making/analytic-hierarchy-process-ahp)  
29. Analytic Hierarchy Process | TransparentChoice, accessed on July 31, 2025, [https://www.transparentchoice.com/analytic-hierarchy-process](https://www.transparentchoice.com/analytic-hierarchy-process)  
30. Analytic Hierarchy Process AHP Tutorial: Consistency Index and Consistency Ratio \- Micro-PedSim, accessed on July 31, 2025, [https://people.revoledu.com/kardi/tutorial/AHP/Consistency.htm](https://people.revoledu.com/kardi/tutorial/AHP/Consistency.htm)  
31. The Analytic Hierarchy Process \- The Systems Engineering Tool Box, accessed on July 31, 2025, [https://www.burgehugheswalsh.co.uk/Uploaded/1/Documents/Analytic-Hierarchy-Process-Tool-v2.pdf](https://www.burgehugheswalsh.co.uk/Uploaded/1/Documents/Analytic-Hierarchy-Process-Tool-v2.pdf)  
32. AHP Consistency Check \- YouTube, accessed on July 31, 2025, [https://www.youtube.com/watch?v=ecckslwG3xk](https://www.youtube.com/watch?v=ecckslwG3xk)  
33. Consistency ratio and Transitivity Rule. \- SpiceLogic, accessed on July 31, 2025, [https://www.spicelogic.com/docs/ahpsoftware/intro/ahp-consistency-ratio-transitivity-rule-388](https://www.spicelogic.com/docs/ahpsoftware/intro/ahp-consistency-ratio-transitivity-rule-388)  
34. medium.com, accessed on July 31, 2025, [https://medium.com/operations-research-bit/a-step-by-step-guide-to-ahp-24c26fc1850b](https://medium.com/operations-research-bit/a-step-by-step-guide-to-ahp-24c26fc1850b)  
35. Analytic Hierarchy Process \- Definitive, accessed on July 31, 2025, [https://definitiveinc.com/definitive-pro/analytic-hierarchy-process/](https://definitiveinc.com/definitive-pro/analytic-hierarchy-process/)  
36. The AHP Pairwise Process. How the Analytic Hierarchy Process… | by Bill Adams | DLProdTeam | Medium, accessed on July 31, 2025, [https://medium.com/dlprodteam/the-ahp-pairwise-process-c639eadcbd0e](https://medium.com/dlprodteam/the-ahp-pairwise-process-c639eadcbd0e)  
37. Cost-Benefit Analysis: 5 Steps to Better Choices \[2025\] • Asana, accessed on July 31, 2025, [https://asana.com/resources/cost-benefit-analysis](https://asana.com/resources/cost-benefit-analysis)  
38. Process customization and inherited processes \- Azure DevOps Services | Microsoft Learn, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/inheritance-process-model?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/inheritance-process-model?view=azure-devops)  
39. Add a custom field to an inherited process \- Azure DevOps Services \- Learn Microsoft, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/add-custom-field?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/add-custom-field?view=azure-devops)  
40. Add and Manage Fields for an Inherited Process \- Azure DevOps ..., accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/customize-process-field?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/customize-process-field?view=azure-devops)  
41. Add custom work item type to inherited process \- Azure DevOps Services \- Learn Microsoft, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/add-custom-wit?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/organizations/settings/work/add-custom-wit?view=azure-devops)  
42. Display rollup columns to show progress, counts, or totals in Azure ..., accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/display-rollup?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/display-rollup?view=azure-devops)  
43. Support for calculated fields and roll-ups \- Visual Studio Developer Community, accessed on July 31, 2025, [https://developercommunity.visualstudio.com/idea/365423/support-calculated-fields-in-tfs.html](https://developercommunity.visualstudio.com/idea/365423/support-calculated-fields-in-tfs.html)  
44. Adding Work Item Age to your Azure DevOps board using Power ..., accessed on July 31, 2025, [https://nbrown02.medium.com/adding-work-item-age-to-your-azure-devops-board-using-power-automate-5b645d02f9ee](https://nbrown02.medium.com/adding-work-item-age-to-your-azure-devops-board-using-power-automate-5b645d02f9ee)  
45. Automating Notifications in Azure Devops Using Power Automate \- Alfero Chingono, accessed on July 31, 2025, [https://www.chingono.com/blog/2024/10/08/automating-notifications-in-azure-devops-using-power-automate/](https://www.chingono.com/blog/2024/10/08/automating-notifications-in-azure-devops-using-power-automate/)  
46. Azure DevOps \- Connectors | Microsoft Learn, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/connectors/visualstudioteamservices/](https://learn.microsoft.com/en-us/connectors/visualstudioteamservices/)  
47. Using Forms to Update Work Items in DevOps | Microsoft Community Hub, accessed on July 31, 2025, [https://techcommunity.microsoft.com/discussions/microsoftforms/using-forms-to-update-work-items-in-devops/3656312](https://techcommunity.microsoft.com/discussions/microsoftforms/using-forms-to-update-work-items-in-devops/3656312)  
48. Get started with the REST APIs for Azure DevOps \- Microsoft Learn, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/integrate/how-to/call-rest-api?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/integrate/how-to/call-rest-api?view=azure-devops)  
49. Azure DevOps Services REST API Reference \- Microsoft Learn, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/rest/api/azure/devops/?view=azure-devops-rest-7.2](https://learn.microsoft.com/en-us/rest/api/azure/devops/?view=azure-devops-rest-7.2)  
50. How to update the workitem using query? \- Visual Studio Developer Community, accessed on July 31, 2025, [https://developercommunity.visualstudio.com/content/problem/1192163/how-to-update-the-workitem-using-query.html](https://developercommunity.visualstudio.com/content/problem/1192163/how-to-update-the-workitem-using-query.html)  
51. REST API (Azure DevOps Work Item Tracking) \- Learn Microsoft, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items?view=azure-devops-rest-7.1](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items?view=azure-devops-rest-7.1)  
52. List \- REST API (Azure DevOps Work Item Tracking) | Microsoft Learn, accessed on July 31, 2025, [https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/list?view=azure-devops-rest-7.1](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/list?view=azure-devops-rest-7.1)  
53. How to edit a field value with Azure DevOps API REST \- Stack Overflow, accessed on July 31, 2025, [https://stackoverflow.com/questions/76868326/how-to-edit-a-field-value-with-azure-devops-api-rest](https://stackoverflow.com/questions/76868326/how-to-edit-a-field-value-with-azure-devops-api-rest)  
54. Work Items \- Update \- REST API (Azure DevOps Work Item Tracking ..., accessed on July 31, 2025, [https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.1](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/update?view=azure-devops-rest-7.1)  
55. Power BI integration and supported connections methods \- Azure ..., accessed on July 31, 2025, [https://learn.microsoft.com/en-us/azure/devops/report/powerbi/overview?view=azure-devops](https://learn.microsoft.com/en-us/azure/devops/report/powerbi/overview?view=azure-devops)  
56. Analytic Hierarchy Process Prioritize Projects | PMI, accessed on July 31, 2025, [https://www.pmi.org/learning/library/analytic-hierarchy-process-prioritize-projects-6608](https://www.pmi.org/learning/library/analytic-hierarchy-process-prioritize-projects-6608)