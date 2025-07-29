// Reference collection and linking - UPDATED to use jsonld library and proper linked field detection
import { Utils } from './utils.js';

export class ReferenceManager {
  constructor(prefixMapping) {
    this.prefixMapping = prefixMapping;
    this.resolvedContext = {};
    this.linkProperties = new Set();
    this.contextTermDefinitions = new Map(); // Store full term definitions from context
  }

  // Set the resolved context for link detection - UPDATED to use jsonld library
  async setResolvedContext(context) {
    console.log('🔗 === SETTING RESOLVED CONTEXT ===');
    console.log('🔗 Context keys:', Object.keys(context || {}));
    console.log('🔗 Context sample:', context);
    
    this.resolvedContext = context;
    
    // Use the jsonld library to process the context and identify linked properties
    await this.identifyLinkPropertiesWithJsonLD(context);
    
    // Enhanced logging
    console.log(`🔗 Link properties identified (${this.linkProperties.size}): ${Array.from(this.linkProperties).join(', ')}`);
    
    if (this.linkProperties.size === 0) {
      console.warn('⚠️ No link properties identified! This might indicate a problem with context resolution.');
    }
  }

  // Use jsonld library to properly identify link properties from context
  async identifyLinkPropertiesWithJsonLD(context) {
    const linkProps = new Set();
    this.contextTermDefinitions.clear();
    
    try {
      // Use jsonld.processContext to get proper term definitions
      const processedContext = await jsonld.processContext({}, context);
      
      console.log('🔗 Processed context with jsonld library:', processedContext);
      
      // Examine the processed context to find terms with @type: @id
      const termDefinitions = processedContext.mappings || {};
      
      for (const [term, definition] of Object.entries(termDefinitions)) {
        // Store the full term definition
        this.contextTermDefinitions.set(term, definition);
        
        // Check if this term has @type: @id (indicates it's a link property)
        if (definition && typeof definition === 'object') {
          if (definition['@type'] === '@id') {
            linkProps.add(term);
            console.log(`🔗 Found link property from jsonld processing: ${term} (has @type: @id)`);
          }
          // Also check if the definition has nested @context with @type: @id
          else if (definition['@context'] && typeof definition['@context'] === 'object') {
            // This term has its own scoped context - check if it defines link behavior
            const scopedContext = definition['@context'];
            if (scopedContext['@type'] === '@id') {
              linkProps.add(term);
              console.log(`🔗 Found link property with scoped context: ${term} (scoped context has @type: @id)`);
            }
          }
        }
      }
      
    } catch (jsonldError) {
      console.warn('⚠️ Failed to process context with jsonld library:', jsonldError.message);
      console.log('🔄 Falling back to manual context analysis...');
      
      // Fallback to manual analysis
      this.identifyLinkPropertiesManually(context, linkProps);
    }
    
    // Store the identified link properties
    this.linkProperties = linkProps;
    
    console.log(`🔗 Total link properties identified: ${linkProps.size}`);
  }

  // Fallback manual identification of link properties - UPDATED to be more precise
  identifyLinkPropertiesManually(context, linkProps) {
    for (const [key, value] of Object.entries(context)) {
      // Skip JSON-LD keywords and 'id' field
      if (key.startsWith('@') || key === 'id') {
        continue;
      }
      
      // ONLY identify as link properties if they explicitly have @type: @id or nested @context
      if (typeof value === 'object' && value !== null) {
        // CASE 1: Object with @type: @id
        if (value['@type'] === '@id') {
          linkProps.add(key);
          console.log(`🔗 Found link property (manual): ${key} (has @type: @id)`);
        }
        // CASE 2: Object with nested @context
        else if (value['@context']) {
          linkProps.add(key);
          console.log(`🔗 Found link property (manual): ${key} (has nested @context)`);
        }
      }
      // Do NOT add string mappings or other types as link properties
      // Only explicit @type: @id or nested @context should be considered linked
    }
  }

  // Check if a key (compacted or expanded) represents a linked property
  isLinkedProperty(key) {
    // Direct check for compacted names
    if (this.linkProperties && this.linkProperties.has(key)) {
      return true;
    }
    
    // Check if this is an expanded URI that maps to a linked property
    if (this.contextTermDefinitions.has(key)) {
      return this.linkProperties.has(key);
    }
    
    // For expanded IRIs, check if any of our link properties expand to this IRI
    for (const linkProp of this.linkProperties) {
      const termDef = this.contextTermDefinitions.get(linkProp);
      if (termDef && termDef['@id'] === key) {
        return true;
      }
    }
    
    return false;
  }

  // Expand a reference using context with jsonld library when possible
  async expandReference(value, key = null) {
    if (!value || typeof value !== 'string') return value;
    
    // Already a full URL
    if (value.startsWith('http')) return value;
    
    try {
      // Try to use jsonld library for proper expansion
      const mockDoc = {};
      if (key) {
        mockDoc[key] = value;
      } else {
        mockDoc['@id'] = value;
      }
      
      const expanded = await jsonld.expand(mockDoc, { '@context': this.resolvedContext });
      
      if (expanded && expanded.length > 0) {
        const expandedDoc = expanded[0];
        if (key && expandedDoc[this.getExpandedKey(key)]) {
          const expandedValue = expandedDoc[this.getExpandedKey(key)];
          if (Array.isArray(expandedValue) && expandedValue.length > 0 && expandedValue[0]['@id']) {
            const result = expandedValue[0]['@id'];
            console.log(`🔗 Expanding reference '${value}' using jsonld library: ${result}`);
            return result;
          }
        } else if (expandedDoc['@id']) {
          const result = expandedDoc['@id'];
          console.log(`🔗 Expanding reference '${value}' using jsonld library: ${result}`);
          return result;
        }
      }
    } catch (jsonldError) {
      console.warn(`⚠️ jsonld expansion failed for '${value}':`, jsonldError.message);
    }
    
    // Fallback to manual expansion
    return this.expandReferenceManually(value, key);
  }

  // Get the expanded form of a key
  getExpandedKey(key) {
    const termDef = this.contextTermDefinitions.get(key);
    if (termDef && termDef['@id']) {
      return termDef['@id'];
    }
    
    // Check for direct string mapping in context
    if (this.resolvedContext[key] && typeof this.resolvedContext[key] === 'string') {
      return this.resolvedContext[key];
    }
    
    return key;
  }

  // Manual expansion fallback with proper priority and correct prefix resolution
  expandReferenceManually(value, key = null) {
    if (!value || typeof value !== 'string') return value;
    
    // Already a full URL
    if (value.startsWith('http')) return value;
    
    // PRIORITY 1: Handle prefixed values FIRST (before property-scoped contexts)
    if (value.includes(':')) {
      const colonIndex = value.indexOf(':');
      const prefix = value.substring(0, colonIndex);
      const suffix = value.substring(colonIndex + 1);
      
      console.log(`🔗 Processing prefixed reference: prefix='${prefix}', suffix='${suffix}'`);
      
      // Check context for prefix mapping first
      if (this.resolvedContext && this.resolvedContext[prefix]) {
        const prefixMapping = this.resolvedContext[prefix];
        if (typeof prefixMapping === 'string') {
          const expanded = prefixMapping + suffix;
          console.log(`🔗 Expanding prefixed reference '${value}' using context prefix '${prefix}': ${expanded}`);
          return expanded;
        }
      }
      
      // Check global prefix mappings
      if (this.prefixMapping.hasOwnProperty(prefix)) {
        const expanded = Utils.resolvePrefix(value, this.prefixMapping);
        console.log(`🔗 Expanding prefixed reference '${value}' using global prefix '${prefix}': ${expanded}`);
        return expanded;
      }
      
      console.log(`⚠️ No prefix mapping found for '${prefix}' in reference '${value}'`);
    }
    
    // PRIORITY 2: Check if this property has its own resolved context (for non-prefixed values)
    if (key && this.resolvedContext && this.resolvedContext[key] && typeof this.resolvedContext[key] === 'object') {
      const propertyDef = this.resolvedContext[key];
      
      // Check if we have a resolved property-specific context
      if (propertyDef['@resolvedContext']) {
        const propContext = propertyDef['@resolvedContext'];
        console.log(`🔗 Using resolved property-specific context for '${key}' to expand '${value}'`);
        
        // Check for exact mapping in property context
        if (propContext[value]) {
          const mapping = propContext[value];
          if (typeof mapping === 'string') {
            console.log(`🔗 Expanding reference '${value}' using property-specific direct mapping: ${mapping}`);
            return mapping;
          } else if (typeof mapping === 'object' && mapping !== null && mapping['@id']) {
            console.log(`🔗 Expanding reference '${value}' using property-specific object mapping: ${mapping['@id']}`);
            return mapping['@id'];
          }
        }
        
        // Use property-specific base/vocab
        const propBase = propContext['@base'];
        const propVocab = propContext['@vocab'];
        
        if (propBase && !value.startsWith('/')) {
          const expanded = propBase + (propBase.endsWith('/') ? '' : '/') + value;
          console.log(`🔗 Expanding '${value}' using property-specific @base: ${expanded}`);
          return expanded;
        } else if (propVocab) {
          const expanded = propVocab + value;
          console.log(`🔗 Expanding '${value}' using property-specific @vocab: ${expanded}`);
          return expanded;
        }
      }
    }
    
    // PRIORITY 3: Check for exact context mapping in main context
    if (this.resolvedContext && this.resolvedContext[value]) {
      const mapping = this.resolvedContext[value];
      if (typeof mapping === 'string') {
        console.log(`🔗 Expanding reference '${value}' using direct context mapping: ${mapping}`);
        return mapping;
      } else if (typeof mapping === 'object' && mapping !== null && mapping['@id']) {
        console.log(`🔗 Expanding reference '${value}' using context object mapping: ${mapping['@id']}`);
        return mapping['@id'];
      }
    }
    
    // PRIORITY 4: Use main context @base or @vocab (only if no direct mapping found)
    if (this.resolvedContext) {
      const baseOrVocab = this.resolvedContext['@base'] || this.resolvedContext['@vocab'];
      if (baseOrVocab) {
        const expanded = baseOrVocab + value;
        console.log(`🔗 Expanding '${value}' using global base/vocab: ${expanded}`);
        return expanded;
      }
    }
    
    // Return original value if no expansion possible
    console.log(`⚠️ No expansion found for reference '${value}', keeping original`);
    return value;
  }

  // Find and collect all @id references that need resolution - UPDATED to only collect from linked properties
  collectIdReferences(obj, refs = new Set(), visited = new Set()) {
    if (typeof obj !== 'object' || obj === null || visited.has(obj)) {
      return refs;
    }
    visited.add(obj);

    if (Array.isArray(obj)) {
      obj.forEach(item => this.collectIdReferences(item, refs, visited));
    } else {
      // Direct @id references in objects that only have @id
      if (obj['@id'] && typeof obj['@id'] === 'string' && Object.keys(obj).length <= 3) {
        if (this.isValidReference(obj['@id'])) {
          refs.add(obj['@id']);
        }
      }

      // String values in properties marked as links in the context (using proper JSON-LD detection)
      Object.entries(obj).forEach(([key, value]) => {
        // ONLY collect references from properties that are actually defined as linked in the context
        if (this.isLinkedProperty(key)) {
          if (typeof value === 'string') {
            const expandedValue = this.expandReferenceManually(value, key);
            if (this.isValidReference(expandedValue, this.resolvedContext)) {
              console.log(`🔗 Collecting linked reference in '${key}': ${value} -> ${expandedValue}`);
              refs.add(expandedValue);
            }
          } else if (Array.isArray(value)) {
            value.forEach(item => {
              if (typeof item === 'string') {
                const expandedValue = this.expandReferenceManually(item, key);
                if (this.isValidReference(expandedValue, this.resolvedContext)) {
                  console.log(`🔗 Collecting linked reference in '${key}[]': ${item} -> ${expandedValue}`);
                  refs.add(expandedValue);
                }
              } else if (typeof item === 'object' && item !== null && item['@id'] && Object.keys(item).length <= 3) {
                if (this.isValidReference(item['@id'])) {
                  refs.add(item['@id']);
                }
              } else if (typeof item === 'object') {
                this.collectIdReferences(item, refs, visited);
              }
            });
          }
        } else if (typeof value === 'object' && value !== null) {
          this.collectIdReferences(value, refs, visited);
        }
      });
    }

    visited.delete(obj);
    return refs;
  }

  // Check if a reference is valid and resolvable with proper priority
  isValidReference(value, context = null) {
    if (!value || typeof value !== 'string') return false;
    
    // Already a full URL
    if (value.startsWith('http')) return true;
    
    // Check for explicit context mapping
    const checkContext = context || this.resolvedContext;
    if (checkContext && checkContext[value]) {
      const mapping = checkContext[value];
      if (typeof mapping === 'string' || (typeof mapping === 'object' && mapping !== null && mapping['@id'])) {
        return true;
      }
    }
    
    // Check for prefixed references
    if (value.includes(':')) {
      const prefix = value.split(':')[0];
      
      // Check context for prefix
      if (checkContext && checkContext[prefix]) {
        return true;
      }
      
      // Check global prefix mappings
      return this.prefixMapping.hasOwnProperty(prefix);
    }
    
    // If we have context with @base or @vocab, even simple strings can be references
    if (checkContext && (checkContext['@base'] || checkContext['@vocab'])) {
      return true;
    }
    
    return false;
  }

  // Collect all @id references from the data structure for iterative processing - UPDATED
  collectAllIdReferences(obj, refs = new Set(), visited = new Set()) {
    if (typeof obj !== 'object' || obj === null || visited.has(obj)) {
      return refs;
    }
    visited.add(obj);

    if (Array.isArray(obj)) {
      obj.forEach(item => this.collectAllIdReferences(item, refs, visited));
    } else {
      // Look for @id keys in objects that need expansion
      if (obj['@id'] && typeof obj['@id'] === 'string') {
        if (this.shouldExpandReference(obj)) {
          refs.add(obj['@id']);
        }
      }

      // Look for string values that are references - ONLY in linked properties
      Object.entries(obj).forEach(([key, value]) => {
        if (typeof value === 'string' && this.isExpandableReference(value, key)) {
          const expandedValue = this.expandReferenceManually(value, key);
          console.log(`🔗 Found expandable reference in '${key}': ${value} -> ${expandedValue}`);
          refs.add(expandedValue);
        } else if (Array.isArray(value)) {
          value.forEach((item, index) => {
            if (typeof item === 'string' && this.isExpandableReference(item, key)) {
              const expandedValue = this.expandReferenceManually(item, key);
              console.log(`🔗 Found expandable reference in '${key}[${index}]': ${item} -> ${expandedValue}`);
              refs.add(expandedValue);
            } else if (typeof item === 'object') {
              this.collectAllIdReferences(item, refs, visited);
            }
          });
        } else if (typeof value === 'object' && value !== null) {
          this.collectAllIdReferences(value, refs, visited);
        }
      });
    }

    visited.delete(obj);
    return refs;
  }

  // Check if a reference object should be expanded
  shouldExpandReference(obj) {
    if (!obj['@id']) return false;
    if (obj['@type']) return false; // Already expanded
    
    const keys = Object.keys(obj);
    if (keys.length > 3) return false; // Too many properties, likely expanded
    
    return this.isExpandableReference(obj['@id'], '@id');
  }

  // Check if a string value is an expandable reference - UPDATED to only expand linked properties
  isExpandableReference(value, key) {
    if (typeof value !== 'string') return false;
    if (['@context', '@base', '@vocab', 'id', '@id'].includes(key)) return false;
    
    // CRITICAL: Only expand references in properties that are defined as linked in the context
    if (key !== '@id' && !this.isLinkedProperty(key)) {
      return false;
    }
    
    // PRIORITY 1: Check for explicit context mapping
    if (this.resolvedContext && this.resolvedContext[value]) {
      const mapping = this.resolvedContext[value];
      if (typeof mapping === 'string' || (typeof mapping === 'object' && mapping !== null && mapping['@id'])) {
        console.log(`🔗 '${value}' is expandable via direct context mapping`);
        return true;
      }
    }
    
    // PRIORITY 2: Check if the value looks like a reference
    if (value.startsWith('http')) {
      return true;
    }
    
    if (value.includes(':')) {
      const prefix = value.split(':')[0];
      
      // Check context for prefix
      if (this.resolvedContext && this.resolvedContext[prefix]) {
        console.log(`🔗 '${value}' is expandable via context prefix mapping`);
        return true;
      }
      
      // Check global prefix mappings
      if (this.prefixMapping.hasOwnProperty(prefix)) {
        console.log(`🔗 '${value}' is expandable via global prefix mapping`);
        return true;
      }
    }
    
    // PRIORITY 3: Check if we have base/vocab that could expand this
    if (this.resolvedContext && (this.resolvedContext['@base'] || this.resolvedContext['@vocab'])) {
      console.log(`🔗 '${value}' might be expandable via base/vocab`);
      return true;
    }
    
    return false;
  }
}