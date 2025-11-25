# Cost Calculation Implementation Plan

## 🚨 CRITICAL: Prevent Explosive Costs

**Problem:** Batch processing AI renders without cost awareness could result in surprise bills.

**Solution:** Real-time cost estimation and safeguards before ANY job runs.

---

## Phase 1: AI Render Plugin Installation

### 1.1 Install on Pod
- Download AI Render from GitHub
- Install to `/workspace/.config/blender/4.0/scripts/addons/`
- Configure API keys (DreamStudio, Stability AI)
- Test headless functionality

### 1.2 Verify Providers
- Test DreamStudio API connection
- Test Stability AI API connection
- Confirm local (RunPod GPU) rendering works

---

## Phase 2: Cost Calculation Module

### 2.1 Core Module (`shared/cost_calculator.py`)

```python
class CostCalculator:
    def __init__(self, config_file='cost_config.yaml'):
        # Load pricing from config
        
    def estimate_render_cost(self, provider, resolution, steps, model, count=1):
        # Returns: {"total": 0.50, "per_image": 0.05, "breakdown": {...}}
        
    def get_provider_pricing(self, provider):
        # Returns current pricing for provider
        
    def validate_job_cost(self, estimated_cost, max_cost=10.0):
        # Returns: True/False, warning message
```

### 2.2 Pricing Config (`shared/cost_config.yaml`)

```yaml
providers:
  dreamstudio:
    base_cost: 0.002  # per image
    cost_per_step: 0.00001
    resolution_multipliers:
      512x512: 1.0
      1024x1024: 4.0
      
  stability:
    base_cost: 0.003
    models:
      sd_1_5: 1.0
      sdxl: 2.0
      
  local:
    api_cost: 0.0
    gpu_cost_per_hr: 0.42
    avg_render_time_sec: 5
```

### 2.3 Usage Example

```python
from cost_calculator import CostCalculator

calc = CostCalculator()

# Estimate cost before job
cost = calc.estimate_render_cost(
    provider='dreamstudio',
    resolution='1024x1024',
    steps=50,
    model='sdxl',
    count=100  # Batch of 100 images
)

print(f"Total: ${cost['total']:.2f}")
# Output: "Total: $60.00"

# Validate against limit
is_safe, message = calc.validate_job_cost(cost['total'], max_cost=50.0)
if not is_safe:
    print(f"⚠️ {message}")
    # Show confirmation dialog
```

---

## Phase 3: Dashboard Integration

### 3.1 Job Submission Form Updates

**Add to form:**
- Provider dropdown: [Local GPU, DreamStudio, Stability AI]
- Resolution: [512x512, 1024x1024, 2048x2048]
- Steps: [20, 30, 50, 100]
- Model: [SD 1.5, SDXL, etc.]
- **Estimated Cost (live update):**
  ```
  💰 Estimated Cost: $12.50
  (100 images × $0.125 each)
  ```

### 3.2 Cost Display Component

```html
<div class="cost-estimate">
  <div class="cost-header">💰 Estimated Cost</div>
  <div class="cost-total">$12.50</div>
  <div class="cost-breakdown">
    • Provider: DreamStudio
    • Resolution: 1024×1024 (4× multiplier)
    • Steps: 50 ($0.0005/step)
    • Count: 100 images
  </div>
  <div class="cost-warning" *ngIf="cost > threshold">
    ⚠️ High cost detected! Confirm before proceeding.
  </div>
</div>
```

### 3.3 Real-Time Cost Updates

```javascript
// Update cost estimate as user changes form
function updateCostEstimate() {
    const provider = document.getElementById('provider').value;
    const resolution = document.getElementById('resolution').value;
    const steps = document.getElementById('steps').value;
    const count = document.getElementById('characterCount').value;
    
    fetch('/api/cost/estimate', {
        method: 'POST',
        body: JSON.stringify({provider, resolution, steps, count})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('costTotal').textContent = `$${data.total.toFixed(2)}`;
        // Show warning if > $50
        if (data.total > 50) {
            showCostWarning(data.total);
        }
    });
}
```

---

## Phase 4: Safeguards

### 4.1 Pre-Submission Validation

```python
@app.route('/api/jobs', methods=['POST'])
def submit_job():
    # Calculate cost
    cost = calc.estimate_render_cost(...)
    
    # Check against limit
    MAX_JOB_COST = 100.0  # $100 max per job
    if cost['total'] > MAX_JOB_COST:
        return jsonify({
            "error": f"Job cost (${cost['total']:.2f}) exceeds limit (${MAX_JOB_COST})",
            "requires_confirmation": True
        }), 400
    
    # Proceed with job...
```

### 4.2 Confirmation Dialog

For high-cost jobs, show confirmation:
```
⚠️ High Cost Job

Estimated cost: $125.00
Provider: DreamStudio
Images: 500
Resolution: 1024×1024

This exceeds the $100 safety limit.

[Cancel] [I Understand, Proceed Anyway]
```

### 4.3 Running Total Tracker

During batch processing, show:
```
🔄 Batch Processing: 45/100 images
💰 Cost so far: $5.62 / $12.50 estimated
⏱️ Time remaining: ~5 minutes
```

---

## Phase 5: Testing & Validation

### 5.1 Unit Tests
- Test cost calculations against known pricing
- Test safeguards (reject > limit)
- Test provider switching

### 5.2 Integration Tests
- Submit small test job (1 image)
- Verify actual cost matches estimate
- Update pricing if discrepancies found

### 5.3 Load Tests
- Batch of 100 images
- Monitor actual vs estimated cost
- Refine formulas

---

## Implementation Order

1. ✅ **Pod is running** (done!)
2. ⬜ Install AI Render plugin on pod
3. ⬜ Build `CostCalculator` class
4. ⬜ Create `cost_config.yaml` with current pricing
5. ⬜ Add `/api/cost/estimate` endpoint to dashboard
6. ⬜ Update job submission form with cost estimate
7. ⬜ Add safeguards (max cost limits)
8. ⬜ Test with 1 image, then 10, then 100
9. ⬜ Refine pricing based on actual costs

---

**Ready to start?** Let's begin with installing AI Render on the pod!

