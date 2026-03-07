Here is an exhaustive breakdown of the provided dashboard image, followed by a mapping strategy to adapt it to your specific data model and requirements.

### Layout Blueprint

```text
+---------------------------------------------------------------------------------------------+
| Sidebar | Header/Filter Bar                                                                 |
| (Left)  | [Title] [Region] [Month/Year] [Year]    [QAR|USD Toggle] [Gauge] [Refresh Date]  |
|         | [Distributor..] [Line of Biz..] ... (18 Dropdowns total)              [Reset Btn] |
|         |-----------------------------------------------------------------------------------|
|         | [ Sales Header ]            | [ Coverage Header ]       | [ Stock Header ]        |
|         | [Val] [Vol] [MSU]           | [Stores] [Calls] [Lines]..| [Value] [Ageing] [Near] |
|         |-----------------------------|---------------------------|-------------------------|
|         | [KPI] [KPI] [KPI]           | [KPI] [KPI] ...           | [KPI] [KPI] [KPI]       |
|         | [Sub] [Sub] [Sub]           | [Sub] [Sub] ...           | [Sub] [Sub] [Sub]       |
|         |-----------------------------|---------------------------|-------------------------|
|         | [Line Chart] x 3            | [Line Chart] x 5          | [Line Chart] x 3        |
|         |-----------------------------|---------------------------|-------------------------|
|         | [Hierarchical Table Grid]   | [Hierarchical Table Grid] | [Hierarchical Table Grid]
|         | (Sales Data w/ Cell Bars)   | (Coverage Data w/ Bars)   | (Stock Data w/ Bars)    |
+---------------------------------------------------------------------------------------------+

```

---

### Component Inventory

#### 1. Overall Layout

* **Page Layout**: Sidebar + Main Content layout. The main content is a dense, full-width, rigid grid.
* **Vertical Sections (Main Area)**: 4 main vertical tiers (Filter Bar -> Header/KPIs -> Sparkline Charts -> Matrix Tables).
* **Columns**: The main body is split into 3 distinct column groups: **Sales** (approx 30% width), **Coverage** (approx 45% width), and **Stock** (approx 25% width).
* **Header/Toolbar**: Located at the top of the main content area, containing title, filters, and global settings.
* **Spacing**: Very tight gaps (approx 4px-8px) between panels. Zero padding inside the colored header blocks.
* **Backgrounds**: Page background is white. Cards/panels are either white with light gray borders or solid colored headers. The sidebar is dark navy blue.

#### 2. Filter Bar / Global Controls

* **Position**: Top of the main content area, spanning full width.
* **Row 1**:
* Title: "Executive View" (Bold, dark gray) with subtitle "Drive Sales Fundamentals Stronger, Faster & Better" (Small, light gray).
* Text Label: "Middle East" (Magenta).
* Dropdowns (Inline): Country (All), Month & Year (All), Year (2025).
* Toggle Switch: Currency toggle QAR (active, dark blue) / USD (white).
* Chart: Half-donut gauge chart (100.0%, dark blue arc).
* Text: Last Refresh with a small calendar icon (13 Dec 2025 07:11 AM).


* **Rows 2 & 3 (Filter Grid)**:
* Two rows of highly condensed dropdowns (Select inputs with standard down-chevron arrows).
* Labels: Distributor, Line of Business, Supplier, Agency, Category, Segment, Brand, Sub Brand, Promotion, SKU, Retailer Group, Retailer Subgroup, Store, Channel, Sub Channel, City, Area, Salesmen.
* State: All currently set to "All".


* **Button**: A distinct "Reset" button on the far right. Magenta background, white text.
* **Sidebar Labels (Navigation)**: "Distributor" and "Retailer" toggles above the main sidebar navigation.

#### 3. KPI Cards

* **Total KPI Columns**: 11 total metric columns grouped under the 3 main headers.
* **Sales Section** (Dark Slate Blue header: `#33586e`)
* Value (Mn): **24.5M**. Sub-metrics: 10.4M +14.1M (green). Growth: 135.1% (green).
* Volume (Tons): **1005.0**. Sub-metrics: 276.2 +728.8 (green). Growth: 263.9% (green).
* MSU: **137.4**. Sub-metrics: 60.7 +76.7 (green). Growth: 126.5% (green).


* **Coverage Section** (Medium Blue header: `#1763aa`)
* Active Stores: **985**. Sub-metrics: 1076 -91 (red). Growth: -8.5% (red).
* Productive Calls: **6,275**. Sub-metrics: 5,160 +1,115 (green). Growth: 21.6% (green).
* Lines Per Store: **27**. Sub-metrics: 15 +12 (green). Growth: 80.1% (green).
* MSL %: **69.9%**. (No sub-metrics).
* Listing %: **87.6%**. (No sub-metrics).


* **Stock Section** (Teal header: `#14abac`)
* Stock Value: **16.1M**. Sub-metrics: 15.0M +1.2M. Growth: 7.9% (green).
* Ageing: **3,100.1K**. Sub-metrics: 2,849.8K +250.2K. Growth: 8.8% (green).
* Near Expiry: **410.9K**. Sub-metrics: 376.8K +34.1K. Growth: 9.1% (green).


* **Styling**: Values are centered. Big numbers are bold (~18-20px). Sub-metrics are small (~10-11px). Positive numbers are green, negative numbers are red.

#### 4. Charts — Individual Breakdown

* **Chart Type**: Sparkline-style Line Charts.
* **Quantity & Position**: 11 charts, one directly underneath every single KPI column.
* **Axes**: None visible (no X or Y axis lines, labels, or gridlines).
* **Data Series**: 2 series per chart.
* Cyan Line: Current Year.
* Magenta Line: Previous Year.


* **Legend**: Inline, top-left of each small chart cell ("Current Year", "Previous Year" with colored circle markers).
* **Interactions**: None visible (static view).
* **Styling**: Thin lines, no fill, no markers on data points. Contained in white boxes with a 1px solid light gray border separating them.

#### 5. Tables / Data Grids

* **Type**: Hierarchical Matrix visual with embedded data bars.
* **Columns per Section**:
* *Sales*: Distributor (Tree), Value, vs PY (Bar), vs Budget (Bar), Growth % (Text).
* *Coverage*: Distributor (Tree), Active Stores, vs PY (Bar), Productive Calls, vs PY (Bar), Lines Per Store, vs PY (Bar), MSL % (Text), Listing % (Text).
* *Stock*: Distributor (Tree), Stock Value (Bar), vs PY (Bar), Ageing (Bar), vs PY (Bar), Near Expiry (Bar), vs PY (Bar).


* **Row Structure**: Expandable tree structure. Root > Entity > Category > Type > Brand. Icons are standard `[+]` and `[-]` square boxes.
* **Formatting**:
* Alternating row backgrounds (white and very faint gray).
* **In-cell Bars**: These are bullet-graph/data-bar style.
* Green bars spanning right = positive variance.
* Red bars spanning left = negative variance.
* Blue bars = absolute volumes/totals (e.g., Active stores, Productive calls).
* Teal bars = Stock absolute values.


* Headers are bold and white, matching the background color of their parent section.
* Totals row at the bottom is bolded.



#### 6. Typography & Styling

* **Font Family**: Power BI default (Segoe UI, or generic sans-serif).
* **Font Weights**:
* Bold: Main section headers, KPI primary values, Matrix table headers, Sub-totals in matrix.
* Regular: Dropdown labels, matrix data, chart legends.


* **Color Palette**:
* Sidebar BG: Dark Navy (`#1d2b36` approx)
* Sidebar Active/Accents: Magenta (`#ba0d59`)
* Sales Header: Dark Slate Blue (`#335368`)
* Coverage Header: Medium Blue (`#2171b5`)
* Stock Header: Teal (`#00aeb3`)
* Current Year Line / Stock Bars: Cyan (`#29b6f6` approx)
* Previous Year Line: Pink/Magenta (`#d81b60` approx)
* Positive Variance text/bars: Green (`#4caf50`)
* Negative Variance text/bars: Red (`#e53935`)
* Text: Dark Charcoal (`#333333`), Gray (`#777777` for labels)
* Borders: Light Gray (`#e0e0e0`)



#### 7. Icons & Visual Indicators

* Calendar icon next to "Last Refresh".
* Chevron down icons in all filter dropdowns.
* Expand/Collapse `[+]` / `[-]` icons in the matrix table.
* Half-donut gauge icon at the top right.

#### 8. Responsive / Spacing Notes

* **Layout**: Highly rigid CSS Grid. Not designed to stack gracefully on mobile; built for wide desktop screens (1080p+).
* **Padding**: Minimal padding inside cards (approx 8px). Headers have ~4px padding.
* **Scroll**: The tables at the bottom would likely have internal `overflow-y: auto` if fully expanded.

---

### Mapping Table (Adapting to your Data Model)

Your model: Product (name, brand, category), Region, Store, Date, Quantity, Value.
Your filters: Date Range, Brand, Product Category, Region.

| # | Component in Image | Type | My Equivalent | Data Source (My Fields) | Keep / Adapt / Drop |
| --- | --- | --- | --- | --- | --- |
| 1 | Filter Row 1 (Country, M/Y, Year) | Dropdowns | Global Date Filter | Date Range | Keep (Consolidate to Date Range Picker) |
| 2 | Filter Rows 2/3 (Distributor, LOB, etc) | Dropdowns | Brand, Category, Region | Brand, Product Category, Region | Adapt (Drop the rest) |
| 3 | Currency Toggle & Gauge | Controls | None | N/A | Drop |
| 4 | Value (Mn) KPI Card | KPI Card | Total Sales KPI | `SUM(Sales.value)` | Keep |
| 5 | Vol / MSU KPI Cards | KPI Card | YoY Growth %, Top Brand KPI | `Sales.value` (Current vs Prev), `MAX(Brand by Sales)` | Adapt |
| 6 | Sales Line Chart (Value) | Sparkline | Sales trend over time | `SUM(Sales.value)` grouped by `Date` | Adapt (Scale up to larger Line/Area chart) |
| 7 | Sales Table (Matrix) | Matrix Table | Sales by Brand, Sales by Region | `SUM(Sales.value)` grouped by `Brand`, `Region` | Adapt (Convert from Matrix table to Bar Charts) |
| 8 | Active Stores KPI Card | KPI Card | Total Active Stores KPI | `COUNT(DISTINCT Store)` | Keep |
| 9 | Active Stores YoY (Sub-metric) | Text/Trend | YoY Change KPI | `COUNT(DISTINCT Store)` vs Previous Period | Keep |
| 10 | Coverage Line Chart (Stores) | Sparkline | Active stores trend | `COUNT(DISTINCT Store)` grouped by `Date` | Adapt (Scale up to larger Line chart) |
| 11 | Coverage Table (Matrix) | Matrix Table | Active stores by region | `COUNT(DISTINCT Store)` grouped by `Region` | Adapt (Convert to Bar Chart) |
| 12 | Stock Section (KPIs, Charts, Tables) | Various | None | N/A | Drop |
| 13 | Sidebar Navigation | Nav | Dashboard 1 & 2 Nav | Route: `/sales`, `/active-stores` | Keep (Simplify tabs) |

---

### Recommended Component Tree (React/Vite)

Based on your requirement to create two specific dashboards (Sales Overview & Active Stores), here is the adapted React component structure. I recommend using **Recharts** for the charts as it handles React state and responsiveness very well, and CSS Grid for the layout.

```jsx
<App>
  <Sidebar>
     {/* Links for "Sales Overview" and "Active Stores" */}
     <NavLinks /> 
  </Sidebar>
  
  <MainContent>
    <Header>
      <Title>Executive View</Title>
      {/* Reduced to just your 4 filters */}
      <FilterBar>
        <DatePicker filter="Date Range" />
        <Select filter="Region" />
        <Select filter="Product Category" />
        <Select filter="Brand" />
        <Button>Reset</Button>
      </FilterBar>
    </Header>

    {/* Route: /sales */}
    <DashboardLayout gridTemplate="repeat(3, 1fr)">
      <SectionCard title="Sales KPIs" color="#33586e">
        <KPI value="Total Sales" trend="+14.1M" percent="135.1%" />
        <KPI value="YoY Growth %" />
        <KPI value="Top Brand" text="MOON MARK" />
      </SectionCard>
      
      <ChartGrid>
        {/* Adapted from the sparklines and matrix table into actual charts */}
        <Card title="Sales Trend Over Time">
          <AreaChart data={salesTrendData} xAxis="Date" yAxis="Sales" />
        </Card>
        <Card title="Sales by Brand">
          <BarChart data={salesByBrandData} layout="vertical" />
        </Card>
        <Card title="Sales by Region">
          <BarChart data={salesByRegionData} layout="horizontal" />
        </Card>
      </ChartGrid>
    </DashboardLayout>

    {/* Route: /active-stores */}
    <DashboardLayout gridTemplate="repeat(2, 1fr)">
      <SectionCard title="Coverage KPIs" color="#1763aa">
        <KPI value="Total Active Stores" trend="-91" percent="-8.5%" />
        <KPI value="YoY Change" />
      </SectionCard>

      <ChartGrid>
        <Card title="Active Stores Trend">
          <LineChart data={storeTrendData} xAxis="Month" yAxis="Store Count" />
        </Card>
        <Card title="Active Stores by Region">
          <BarChart data={storeByRegionData} layout="vertical" />
        </Card>
      </ChartGrid>
    </DashboardLayout>
  </MainContent>
</App>

```