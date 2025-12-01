param(
	[Parameter(Mandatory=$false)][string]$Message = "",
	[Parameter(Mandatory=$false)][string]$Branch = ""
)

# ...existing code...
try {
	Write-Host "🔍 Checking git repository..." -ForegroundColor Cyan
	# Ensure we are inside a git repo
	$gitDir = git rev-parse --git-dir 2>$null
	if (-not $?) {
		Write-Error "This folder is not a git repository. Initialize with: git init"
		exit 1
	}

	# Determine current branch if none provided
	if ([string]::IsNullOrWhiteSpace($Branch)) {
		$Branch = git rev-parse --abbrev-ref HEAD
	}

	# Stage all changes
	Write-Host "➕ Staging all changes..."
	git add -A
	if (-not $?) { throw "git add failed." }

	# Prepare commit message
	if ([string]::IsNullOrWhiteSpace($Message)) {
		# open editor for message
		Write-Host "✍️  No commit message provided. Opening default editor..."
		git commit
	} else {
		git commit -m $Message
	}

	if (-not $?) {
		Write-Host "ℹ️  Nothing to commit or commit failed." -ForegroundColor Yellow
	} else {
		# Push to origin
		Write-Host "⬆️  Pushing to origin/$Branch ..."
		git push origin $Branch
		if ($LASTEXITCODE -ne 0) {
			Write-Error "git push failed. Check remote and authentication."
			exit 1
		} else {
			Write-Host "✅ Push completed successfully to origin/$Branch" -ForegroundColor Green
		}
	}

} catch {
	Write-Error "Error: $_"
	exit 1
}