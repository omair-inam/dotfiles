---
allowed-tools: Bash(omics:*), Read, Write, Edit, Glob, Grep
description: Create, optimize, or improve Trino SQL queries with performance analysis and testing
---

# Trino SQL Query Development

## Context
* Develop, optimize, or improve Trino SQL queries with focus on performance, correctness, and maintainability.

## Overriding Principles
* Prioritize correctness first, then optimize for performance.
* Write out a detailed plan as a progress tracker and checklist into a markdown file in tasks/ 
  * This file should include:
    * Step-by-step instructions on how to execute the plan
    * Detailed steps/commands to validate the changes
  * The file should be named using the format `YYYYmmdd_hhmmsss-query_name_in_snake_case.md` and placed in the `tasks/` directory.
  * If the `tasks/` directory does not exist, create it.
  * Keep the file updated to reflect any deviations from the plan found during execution, especially noting additional testing steps.
* Use small incremental steps to build or optimize the query.    
  * Before each step, explain what you plan to do and why.  Prompt the user to type "Go" to proceed 
  * After each step, 
     * test the component or CTE individually to ensure correctness.
     * review the explain plan to identify performance bottlenecks.
     * document the changes and reasoning. 

## Input Requirements
$ARGUMENTS

Expected inputs can include:
- **Query description**: Natural language description of what the query should accomplish
- **Existing query**: SQL query that needs optimization or improvement
- **Performance requirements**: Specific performance targets or constraints
- **Test parameters**: Sample data or parameter sets for testing
- **Data schema**: Information about tables, columns, and data types
- **Publisher instance URL**: URL of the DNAstack Publisher instance for testing connectivity and query execution

## Development Process

### 1. Requirements Analysis
- Parse the request to understand query objectives
- Identify input parameters and expected output format
- Convert parameterized queries if necessary.   
- Determine if single-parameter or batch processing is needed
- Assess performance requirements and constraints

#### Parsing parameterized queries
The input query may contain placeholders for parameters.  If so, identify the placeholders and their expected formats.

Placeholders will be specified in the format `{{param_name}}`.  For example:
```sql
SELECT *
FROM variants
WHERE chromosome = '{{chromosome}}'
    AND position = {{position}}
```

In more complicated quries that require batch processing of multiple parameter sets, the input query may contain multiple placeholders
that are part of a CTE that processes comma-separated string parameters.  For example:

```sql
WITH
    -- Input variants from comma-separated string parameters
    input_variants AS (
        SELECT
            c.chromosome,
            CAST(p.position_str AS BIGINT) AS position
        FROM
            UNNEST(split({{chromosome}}, ',')) WITH ORDINALITY AS c(chromosome, idx),
            UNNEST(split({{position}}, ',')) WITH ORDINALITY AS p(position_str, idx2)
        WHERE c.idx = p.idx2
    )

SELECT * from input_variants
```

### 2. Query Design Strategy

#### For New Queries:
- Design optimal query structure with CTEs (Common Table Expressions)
- Plan efficient joins and filtering strategies
- Consider early filtering to reduce dataset size
- Design for proper indexing utilization

#### For Query Optimization:
- Analyze existing query for performance bottlenecks:
  - Cartesian products
  - Full table scans
  - Complex subqueries
  - Missing early filtering
  - Redundant operations
- Identify specific optimization opportunities

### 3. Implementation Approach
* Use small incremental steps to build or optimize the query
* Test each component or CTE individually 
* Incorporate best practices for Trino SQL
* Document the query with comments for clarity

#### Core Optimization Principles:
1. **Early Filtering**: Apply WHERE conditions as early as possible
2. **Avoid Cartesian Products**: Use proper JOIN syntax instead of comma-separated FROM clauses
3. **Minimize Table Scans**: Reuse CTEs and filtered datasets
4. **Proper JOIN Usage**: Use INNER JOIN, LEFT JOIN explicitly
5. **Batch Processing**: Use UNNEST with split() for parameter arrays

#### Common Patterns:
```sql
-- Parameter input pattern for batch processing
input_variants AS (
    SELECT
        c.param1,
        CAST(s.param2_str AS BIGINT) AS param2
    FROM
        UNNEST(split('val1,val2', ',')) WITH ORDINALITY AS c(param1, idx),
        UNNEST(split('123,456', ',')) WITH ORDINALITY AS s(param2_str, idx2)
    WHERE c.idx = s.idx2
),

-- Early filtering pattern
filtered_data AS (
    SELECT columns
    FROM large_table lt
    WHERE lt.filter_column IN (SELECT param FROM input_variants)
)
```

### 4. Testing and Validation
#### Environment Setup: Connecting to a Publisher instance
- A publisher service registry URL is required for testing.  The service registry URL can be derived from a publisher instance URL.  
- Publisher URL: For internal (DNAstack hosted) instances, a Publisher URL typically follows the format `https://publisher.<instance>.dnastack.com`.
- Service Registry URL: The service registry URL can be derived by replacing `publisher` with `collection-service` in the Publisher URL
  and appending `/service-registry/services/` at the end. For example, if the Publisher URL is `https://publisher.core-cleanroom.helm-sandbox.dnastack.com/`, 
  the service registry URL would be `https://collection-service.core-cleanroom.helm-sandbox.dnastack.com/service-registry/services/`.
- To connect to a service registry URL, use the `omics use` command from the DNAstack CLI.  Example:

```bash
omics use https://collection-service.core-cleanroom.helm-sandbox.dnastack.com/service-registry/services/
```
- An `omics use` command may prompt the user to authenticate via device code flow.  If a message like: 
  `Please go to https://wallet.core-cleanroom.helm-sandbox.dnastack.com/authorize?user_code=<code>` is displayed on the console:
  - use the Playwright MCP server and navigate to the URL in a browser
  - prompt the user to complete the authentication and ask them to type 'done' when complete
  - wait for the user to complete authentication.

#### Incremental Testing Strategy:
1. **Component Testing**: Test individual CTEs separately
2. **Parameter Validation**: Verify input parameter parsing
3. **Performance Testing**: Measure execution time with `time` command
4. **Result Validation**: Compare outputs with expected results
5. **Batch Testing**: Test with multiple parameter sets

#### Testing Commands:
```bash
# Test connection
omics dc query "SHOW CATALOGS LIKE '%pattern%'"

# Test filtered dataset size
omics dc query "SELECT COUNT(*) FROM (filtered_cte_query)"

# Execute query (removing all comments)
omics dc query "$(cat query_file.sql | rg -v '^\s*--')"

# Performance timing
time omics dc query "$(cat query_file.sql)"
```

#### Reviewing Explain Plans
* Query plan analysis should be performed exclusively using Trino API calls rather than web UI navigation.
* **Authentication Required**: Before making API calls, prompt the user to provide the required authentication cookies from their browser session.

**Required Authentication Cookies:**
Ask the user to:
1. Open the Trino Web UI in their browser (e.g. https://localhost:8443/ui)
2. Complete authentication if prompted (DNAstack Passport login)
3. Extract the following cookies from their browser developer tools:
   - `__Secure-Trino-ID-Token` 
   - `__Secure-Trino-OAuth2-Token`
4. Provide these cookie values for API authentication

**Step-by-step API-based Query Analysis Process:**

1. **Retrieve Query List**: Get recent queries using API endpoints
   ```bash
   # IMPORTANT: Output can be massive (thousands of queries), always redirect to temp file
   curl -k -H "Cookie: __Secure-Trino-ID-Token={token}; __Secure-Trino-OAuth2-Token={oauth_token}" \
     "https://localhost:8443/ui/api/query" > /tmp/trino_queries.json
   
   # Filter by state if needed (more efficient for large datasets)
   curl -k -H "Cookie: ..." \
     "https://localhost:8443/ui/api/query?state=FINISHED" > /tmp/trino_finished.json
   ```

2. **Search and Filter Queries**: Use command-line tools to find relevant queries
   ```bash
   # Search for queries containing specific SQL patterns
   jq '.[] | select(.queryTextPreview | contains("SELECT")) | {queryId, state, elapsedTime: .queryStats.elapsedTime}' \
     /tmp/trino_queries.json
   
   # Find slow queries (>30 seconds)
   jq '.[] | select(.queryStats.elapsedTime | tonumber > 30) | {queryId, elapsedTime: .queryStats.elapsedTime, queryTextPreview}' \
     /tmp/trino_finished.json
   
   # Filter by user or resource group
   jq '.[] | select(.sessionUser == "dlcon-trino") | {queryId, state, elapsedTime: .queryStats.elapsedTime}' \
     /tmp/trino_queries.json
   ```

3. **Analyze Specific Query Performance**: Get detailed query statistics
   ```bash
   QUERY_ID="20250829_125752_50073_eyzfj"
   curl -k -H "Cookie: ..." \
     "https://localhost:8443/ui/api/query/$QUERY_ID" > /tmp/query_${QUERY_ID}.json
   ```

4. **Extract Key Performance Metrics**:
   ```bash
   # Get execution summary
   jq '{
     queryId: .queryId,
     state: .state,
     elapsedTime: .queryStats.elapsedTime,
     executionTime: .queryStats.executionTime, 
     cpuTime: .queryStats.totalCpuTime,
     memoryPeak: .queryStats.peakUserMemoryReservation,
     inputRows: .queryStats.rawInputPositions,
     inputData: .queryStats.physicalInputDataSize,
     planningTime: .queryStats.planningTime,
     analysisTime: .queryStats.analysisTime
   }' /tmp/query_${QUERY_ID}.json
   
   # Get stage-level performance data
   jq '.outputStage // empty' /tmp/query_${QUERY_ID}.json
   ```

5. **Performance Analysis Focus Areas**:
   - **Execution Time**: `elapsedTime` vs `executionTime` vs `totalCpuTime`
   - **Memory Usage**: `peakUserMemoryReservation` and `cumulativeUserMemory`
   - **Data Processing**: `rawInputPositions` vs output rows, `physicalInputDataSize`
   - **Stage Analysis**: Review `outputStage` for bottlenecks and resource usage
   - **Planning Overhead**: `planningTime` and `analysisTime` relative to total execution

**Available API Endpoints:**
- `GET /ui/api/query`: Retrieves a list of recent queries (can return thousands - always redirect to temp file)
- `GET /ui/api/query?state=<state>`: Retrieves queries filtered by state (more efficient)
  - **Possible states**: QUEUED, WAITING_FOR_RESOURCES, DISPATCHING, PLANNING, STARTING, RUNNING, FINISHING, FINISHED, FAILED  
- `GET /ui/api/query/{queryId}`: Retrieves complete details for a specific query

**API Usage Examples:**
```bash
# IMPORTANT: Always use authentication cookies and redirect large responses to temp files
COOKIES="Cookie: __Secure-Trino-ID-Token={token}; __Secure-Trino-OAuth2-Token={oauth_token}"

# Get all recent queries (MASSIVE OUTPUT - always redirect)
curl -k -H "$COOKIES" "https://localhost:8443/ui/api/query" > /tmp/all_queries.json

# Get finished queries only (more efficient filtering)
curl -k -H "$COOKIES" "https://localhost:8443/ui/api/query?state=FINISHED" > /tmp/finished_queries.json

# Get currently running queries for monitoring
curl -k -H "$COOKIES" "https://localhost:8443/ui/api/query?state=RUNNING"

# Get specific query with full execution plan
curl -k -H "$COOKIES" "https://localhost:8443/ui/api/query/20250829_125752_50073_eyzfj" > /tmp/query_details.json
```

**Common Performance Issues to Look For**:
- **High Blocked Time**: Indicates resource contention or inefficient joins
- **Memory Spilling**: Peak memory usage exceeding available resources
- **Uneven Stage Distribution**: Some stages processing significantly more data
- **Excessive Data Movement**: Large amounts of data being shuffled between stages
- **Table Scan Inefficiency**: Full table scans when filtered scans would be better


### 5. Performance Analysis

#### Key Metrics:
- **Execution Time**: Target <30 seconds for batch queries
- **Dataset Size**: Monitor intermediate result set sizes
- **Resource Usage**: Memory and CPU utilization patterns
- **Scalability**: Ability to handle larger parameter batches

#### Optimization Techniques:
- **Dataset Reduction**: Early filtering can reduce datasets by 95%+
- **Join Optimization**: Proper JOIN syntax enables query planner optimization
- **CTE Reuse**: Share filtered datasets across multiple operations
- **Index Utilization**: Leverage existing table indexes with proper WHERE clauses

### 6. Documentation and Output

#### Query Documentation:
```sql
-- Query Purpose: [Clear description]
-- Performance: [Execution time, dataset size]
-- Parameters: [Input format and examples]
-- Test Cases: [Sample parameter sets]
```

#### Results Summary:
- **Performance Metrics**: Execution time, dataset size
- **Correctness Validation**: Result comparison with test cases
- **Usage Examples**: Sample parameter sets and expected outputs
- **Maintenance Notes**: Key optimization points and potential issues

## Output Format

### For New Queries:
1. **Optimized SQL Query** (with and without comments)
2. **Performance Analysis** (execution time, dataset reduction)
3. **Test Results** (validation with sample parameters)
4. **Usage Documentation** (parameter format, examples)

### For Query Optimization:
1. **Before/After Performance Comparison**
2. **Optimization Techniques Applied**
3. **Result Validation** (ensuring identical outputs)
4. **Scalability Assessment** (handling larger batches)

## Best Practices

### SQL Style:
- Use meaningful CTE names that describe their purpose
- Proper indentation and formatting for readability
- Clear column aliases with descriptive names
- Comments for complex logic sections

### Performance:
- Always test queries with realistic data sizes
- Monitor for timeout issues and memory constraints
- Design for batch processing from the start
- Consider query plan implications of JOIN order

### Maintainability:
- Parameterize values rather than hardcoding
- Use consistent naming conventions
- Document complex business logic
- Plan for future scalability needs

## Notes
- Focus on Trino-specific optimizations and limitations
- Consider data catalog structure and available indexes
- Account for distributed query processing characteristics
- Prioritize correctness first, then optimize for performance