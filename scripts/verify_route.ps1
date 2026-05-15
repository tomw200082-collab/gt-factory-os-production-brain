$manifest = Get-Content 'C:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION\.lionwheel-prints\2026-05-14-maksim\manifest.json' -Raw | ConvertFrom-Json
$pdfDir = 'C:\Users\tomw2\GTeveryday Dropbox\Data Center\Tom\AI Agents & Projects\Code Agents\PRODUCTION\.lionwheel-prints\2026-05-14-maksim\pdfs'

foreach ($task in $manifest.tasks) {
    $order = $task.route_order
    $name = $task.recipient_name
    $wpid = $task.wp_order_id
    $hasUrl = $task.green_invoice_urls.Count -gt 0
    if ($hasUrl) {
        $pdfPath = Join-Path $pdfDir ($task.task_id + '.pdf')
        if (Test-Path $pdfPath) {
            $size = (Get-Item $pdfPath).Length
            Write-Output "OK   [$order] $name ($wpid) — $size bytes"
        } else {
            Write-Output "MISS [$order] $name ($wpid) — PDF MISSING!"
        }
    } else {
        Write-Output "SKIP [$order] $name ($wpid) — no invoice"
    }
}
