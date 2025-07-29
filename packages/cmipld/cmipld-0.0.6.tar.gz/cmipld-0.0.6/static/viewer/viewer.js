// CMIP-LD Viewer v3 - Updated: Removed depth field, use substitute linked files toggle
import { URLManager } from './modules/url-manager.js';
import { ModuleFactory } from './modules/core/module-factory.js';

export class CMIPLDViewer {
  constructor() {
    this.initializeModules();
    this.initializeFromUrl();
    this.initializeEventListeners();
  }

  // Initialize all modules using the factory pattern
  initializeModules() {
    // Create all modules with proper dependencies
    const modules = ModuleFactory.createModules(this);
    
    // Assign modules to instance properties for easy access
    Object.assign(this, modules);
    
    // Configure relationships between modules
    ModuleFactory.configureModuleRelationships(modules, this);
  }

  // Initialize viewer from URL parameters
  initializeFromUrl() {
    const settings = this.initializationManager.initializeFromUrl();
    
    // Auto-load if URI is provided
    if (this.initializationManager.shouldAutoLoad(settings)) {
      setTimeout(() => this.loadData(), 100);
    }
  }

  // Initialize event listeners
  initializeEventListeners() {
    this.eventManager.initializeEventListeners();
  }

  // Update URL with current settings
  updateUrl() {
    const inputSection = document.getElementById('inputSection');
    const settings = {
      uri: document.getElementById('uri').value.trim(),
      substituteLinkedFiles: document.getElementById('substituteLinkedFiles').checked,
      insertContext: document.getElementById('insertContext').checked,
      isExpanded: this.stateManager.getExpanded(),
      panelMinimized: inputSection?.classList.contains('minimized') || false
    };
    
    URLManager.updateUrl(settings);
  }

  // Main data loading workflow - updated to use substitute toggle
  async loadData() {
    this.uiManager.showLoading(true);

    try {
      // Extract and validate parameters
      const { uri, substituteLinkedFiles } = this.dataLoadingManager.extractFormParameters();
      const validatedUri = this.dataLoadingManager.validateInput(uri);
      
      // Configure enhanced link substitution manager
      this.enhancedLinkSubstitution.setEnabled(substituteLinkedFiles);
      
      // Clear previous data
      this.clearData();
      this.updateUrl();
      
      // Execute the complete load and display workflow
      await this.workflowManager.executeLoadAndDisplayWorkflow(validatedUri, substituteLinkedFiles);
      
      // Set up reference manager with the merged context
      this.referenceManager.setResolvedContext(this.stateManager.getMergedContext());
      
    } catch (error) {
      console.error('❌ Failed to load data:', error);
      this.uiManager.showError(`Failed to load data: ${error.message}`);
    } finally {
      this.uiManager.showLoading(false);
    }
  }

  // Update the view - now delegated to workflow manager
  async updateView() {
    await this.workflowManager.executeViewUpdateWorkflow();
  }

  // UI callback handlers
  rerenderDisplay() {
    this.displayManager.rerenderDisplay(this.stateManager.getCurrentViewData());
  }

  handleFieldExpansion(field, expand) {
    console.log(`🔗 Field expansion request: ${field}, expand: ${expand}`);
    // This could be implemented to dynamically expand/collapse specific fields
    this.rerenderDisplay();
  }

  // Export functions - delegate to export manager
  async copyToClipboard() {
    await this.exportManager.copyToClipboard(this.stateManager.getCurrentViewData());
  }

  downloadJson() {
    this.exportManager.downloadJson(
      this.stateManager.getCurrentViewData(), 
      this.stateManager.getExpanded()
    );
  }

  // Copy the resolved file URL to clipboard
  async copyFileUrl() {
    await this.exportManager.copyFileUrl();
  }

  // Open GitHub repository for the current file
  openGithubRepo() {
    this.exportManager.openGithubRepo();
  }

  // Clear all data and reset state
  clearData() {
    this.stateManager.clearData();
    this.documentLoader.clear();
    this.jsonldProcessor.clear();
    this.jsonRenderer.setOriginalContext(null);
    this.inlineDocumentManager.clearCache();
    this.enhancedLinkSubstitution.clearAll();
  }

  // Getters for backward compatibility and access by event manager
  get isExpanded() {
    return this.stateManager.getExpanded();
  }

  set isExpanded(value) {
    this.stateManager.setExpanded(value);
  }

  get mainDocumentUrl() {
    return this.stateManager.mainDocumentUrl;
  }
}

// Initialize the viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
  window.cmipldViewer = new CMIPLDViewer();
});