/**
 * CLI Example for UPSS
 */

const UPSSLoader = require('./upss-loader');

async function main() {
  try {
    console.log('Loading UPSS configuration...');
    const loader = new UPSSLoader('upss_config.yaml');
    await loader.init();

    console.log('\n' + '='.repeat(50));
    console.log('Available Prompts:');
    console.log('='.repeat(50));

    const prompts = loader.listPrompts();
    for (const promptId of prompts) {
      const metadata = loader.getPromptMetadata(promptId);
      console.log(`\nID: ${promptId}`);
      console.log(`  Type: ${metadata.type}`);
      console.log(`  Version: ${metadata.version}`);
      console.log(`  Description: ${metadata.description || 'N/A'}`);
    }

    console.log('\n' + '='.repeat(50));
    console.log('System Assistant Prompt:');
    console.log('='.repeat(50));
    const systemPrompt = await loader.getPrompt('system_assistant');
    console.log(systemPrompt);

    console.log('\n' + '='.repeat(50));
    console.log('Prompt Integrity:');
    console.log('='.repeat(50));
    const hash = await loader.getPromptHash('system_assistant');
    console.log(`SHA-256: ${hash}`);

    console.log('\n' + '='.repeat(50));
    console.log('Audit Log:');
    console.log('='.repeat(50));
    const auditLog = loader.getAuditLog();
    if (auditLog.length > 0) {
      auditLog.forEach(entry => {
        console.log(`${entry.timestamp} - ${entry.prompt_id}: ${entry.action}`);
      });
    } else {
      console.log('Audit logging is not enabled or no entries recorded.');
    }

    console.log('\n' + '='.repeat(50));
    console.log('Application completed successfully!');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
