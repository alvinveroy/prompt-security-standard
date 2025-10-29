/**
 * UPSS Configuration Loader for JavaScript/Node.js
 * Loads and manages prompt configurations following the Universal Prompt Security Standard.
 */

const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');
const crypto = require('crypto');

class UPSSLoader {
  constructor(configPath) {
    this.configPath = configPath;
    this.configDir = path.dirname(configPath);
    this.config = null;
    this.promptsCache = new Map();
    this.auditLog = [];
  }

  async init() {
    await this._loadConfig();
  }

  async _loadConfig() {
    try {
      const fileContent = await fs.readFile(this.configPath, 'utf8');
      this.config = yaml.load(fileContent);

      if (!this.config) {
        throw new Error('Configuration file is empty');
      }

      if (!this.config.upss_version) {
        throw new Error('Missing required field: upss_version');
      }
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
  }

  async getPrompt(promptId, useCache = true) {
    if (useCache && this.promptsCache.has(promptId)) {
      this._logAccess(promptId, 'cache_hit');
      return this.promptsCache.get(promptId);
    }

    if (!this.config.prompts || !this.config.prompts[promptId]) {
      throw new Error(`Prompt not found: ${promptId}`);
    }

    const promptConfig = this.config.prompts[promptId];
    const promptPath = path.join(this.configDir, promptConfig.path);

    try {
      const content = await fs.readFile(promptPath, 'utf8');
      this.promptsCache.set(promptId, content);
      this._logAccess(promptId, 'loaded');
      return content;
    } catch (error) {
      throw new Error(`Failed to load prompt file: ${error.message}`);
    }
  }

  getPromptMetadata(promptId) {
    if (!this.config.prompts || !this.config.prompts[promptId]) {
      throw new Error(`Prompt not found: ${promptId}`);
    }
    return this.config.prompts[promptId];
  }

  listPrompts() {
    return this.config.prompts ? Object.keys(this.config.prompts) : [];
  }

  async getPromptHash(promptId) {
    const content = await this.getPrompt(promptId);
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  _logAccess(promptId, action) {
    const auditConfig = this.config.audit || {};
    if (!auditConfig.enabled) {
      return;
    }

    this.auditLog.push({
      timestamp: new Date().toISOString(),
      prompt_id: promptId,
      action: action
    });
  }

  getAuditLog() {
    return [...this.auditLog];
  }

  async reload() {
    this.promptsCache.clear();
    await this._loadConfig();
  }
}

module.exports = UPSSLoader;
