from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from colorama import init, Fore, Style
import os
import json
from datetime import datetime

from ...core.sync_engine import SyncEngine
from ...settings import get_setting
from ...utils.helpers import generate_orphaned_models_report

init(autoreset=True)  # Initialize colorama

class Command(BaseCommand):
    help = 'Synchronize Django models with database schema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database alias to use (default: default)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
        parser.add_argument(
            '--auto-approve',
            action='store_true',
            help='Automatically approve all operations without prompting'
        )
        
        parser.add_argument(
            '--exclude-apps',
            nargs='*',
            help='Apps to exclude from synchronization'
        )
        
        parser.add_argument(
            '--include-apps',
            nargs='*',
            help='Apps to include in synchronization (only these will be synced)'
        )
        
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create backup before synchronization'
        )
        
        parser.add_argument(
            '--report',
            choices=['json', 'html', 'both'],
            help='Generate report after synchronization'
        )
        
        parser.add_argument(
            '--show-orphaned',
            action='store_true',
            help='Show orphaned tables after synchronization'
        )
        
        parser.add_argument(
            '--drop-orphaned',
            action='store_true',
            help='Drop orphaned tables (use with caution!)'
        )
        
        parser.add_argument(
            '--exclude-table-patterns',
            nargs='*',
            help='Regex patterns for tables to exclude'
        )
        
        parser.add_argument(
            '--no-restriction',
            action='store_true',
            help='Disable all restrictions and include all models/tables'
        )
        
        parser.add_argument(
            '--exclude-app-patterns',
            nargs='*',
            help='Regex patterns for apps to exclude'
        )
        
        parser.add_argument(
            '--suggest-manual-commands',
            action='store_true',
            help='Show manual SQL commands for table renames (automatically shown in dry-run mode)'
        )
        
        parser.add_argument(
            '--generate-orphaned-models',
            action='store_true',
            help='Generate Django models for orphaned tables'
        )
        
        parser.add_argument(
            '--report-views',
            action='store_true',
            help='Generate a report and Django models for all database views'
        )
        
        parser.add_argument(
            '--list-views',
            action='store_true',
            help='Print the count and names of all database views to the terminal (no file generated)'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        version = get_setting('VERSION', '1.0.0')
        self.stdout.write(
            f"{Fore.CYAN}Django Database Sync v{version}{Style.RESET_ALL}"
        )
        self.stdout.write("=" * 50)
        
        try:
            # Initialize sync engine
            sync_engine = SyncEngine(
                database_alias=options['database'],
                dry_run=options['dry_run'],
                auto_approve=options['auto_approve']
            )
            
            # Configure options
            if options['exclude_apps']:
                sync_engine.set_excluded_apps(options['exclude_apps'])
            
            if options['include_apps']:
                sync_engine.set_included_apps(options['include_apps'])
            
            # Apply regex patterns from command line
            if options['exclude_table_patterns']:
                sync_engine.set_exclude_table_patterns(options['exclude_table_patterns'])
            
            if options['exclude_app_patterns']:
                sync_engine.set_exclude_app_patterns(options['exclude_app_patterns'])
            
            # Handle no-restriction flag
            if options['no_restriction']:
                sync_engine.set_no_restriction(True)
                self.stdout.write(f"{Fore.YELLOW}⚠️  No-restriction mode enabled: ALL Django tables will be synced (including auth, admin, sessions, etc.){Style.RESET_ALL}")
            
            # Create backup if requested
            if options['backup']:
                self.stdout.write(f"{Fore.YELLOW}Creating backup...{Style.RESET_ALL}")
                backup_file = sync_engine.create_backup()
                self.stdout.write(f"{Fore.GREEN}Backup created: {backup_file}{Style.RESET_ALL}")
            
            # Check if we're only dropping orphaned tables
            if options['drop_orphaned'] and not any([
                options['exclude_apps'], options['include_apps'], 
                options['exclude_table_patterns'], options['exclude_app_patterns'],
                options['no_restriction']
            ]):
                # Only handle orphaned tables, don't run full sync
                self.stdout.write(f"{Fore.BLUE}Checking for orphaned tables...{Style.RESET_ALL}")
                orphaned = sync_engine.get_orphaned_tables()
                self._display_orphaned_tables(orphaned)
                
                if orphaned:
                    self._handle_orphaned_tables(sync_engine, orphaned, options['dry_run'])
                else:
                    self.stdout.write(f"{Fore.GREEN}✅ No orphaned tables found!{Style.RESET_ALL}")
                
                results = {}  # Empty results since we didn't run sync
            else:
                # Run full synchronization
                self.stdout.write(f"{Fore.BLUE}Starting synchronization...{Style.RESET_ALL}")
                results = sync_engine.sync_all_models()
                
                # Show results
                self._display_results(results)
            
            # Display manual commands only if --suggest-manual-commands is used
            if options['suggest_manual_commands']:
                sync_engine.display_manual_commands()
            
            # Show orphaned tables if requested (but not if we already handled them above)
            if (options['show_orphaned'] or get_setting('SHOW_ORPHANED_TABLES')) and not options['drop_orphaned']:
                orphaned = sync_engine.get_orphaned_tables()
                self._display_orphaned_tables(orphaned)
            
            # Generate report if requested
            if options['report']:
                self._generate_report(results, options['report'])
            
            # Generate orphaned models report if requested
            if options['generate_orphaned_models']:
                orphaned_tables = sync_engine.get_orphaned_tables()
                if orphaned_tables:
                    output_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
                    filepath = generate_orphaned_models_report(
                        orphaned_tables, 
                        options['database'], 
                        output_dir
                    )
                    if filepath:
                        self.stdout.write(f"{Fore.GREEN}✅ Orphaned models generated: {filepath}{Style.RESET_ALL}")
                else:
                    self.stdout.write(f"{Fore.YELLOW}ℹ️  No orphaned tables found to generate models for{Style.RESET_ALL}")
            
            # Generate views report if requested
            if options['report_views']:
                from ...utils.helpers import generate_views_report
                filepath, views = generate_views_report(options['database'])
                if views:
                    self.stdout.write(f"{Fore.GREEN}✅ Views report generated: {filepath}{Style.RESET_ALL}")
                    self.stdout.write(f"{Fore.CYAN}Database Views:{Style.RESET_ALL}")
                    for view in views:
                        self.stdout.write(f"  - {view['name']} (columns: {', '.join(view['columns'])})")
                else:
                    self.stdout.write(f"{Fore.YELLOW}ℹ️  No views found in the database{Style.RESET_ALL}")
            
            # List views if requested
            if options['list_views']:
                from ...utils.helpers import list_database_views
                view_count, view_names = list_database_views(options['database'], names_only=True)
                self.stdout.write(f"\n{Fore.CYAN}Database Views:{Style.RESET_ALL}")
                self.stdout.write(f"Total Views: {view_count}")
                if view_names:
                    for name in view_names:
                        self.stdout.write(f"- {name}")
                else:
                    self.stdout.write("No views found.")
            
            self.stdout.write(f"{Fore.GREEN}Synchronization completed!{Style.RESET_ALL}")
            
        except Exception as e:
            raise CommandError(f"Sync failed: {e}")
    
    def _display_results(self, results):
        """Display sync results"""
        self.stdout.write(f"\n{Fore.CYAN}Sync Results:{Style.RESET_ALL}")
        self.stdout.write("-" * 30)
        
        for model_name, result in results.items():
            if result['status'] == 'success':
                color = Fore.GREEN
                status = "✅"
            elif result['status'] == 'warning':
                color = Fore.YELLOW  
                status = "⚠️"
            elif result['status'] == 'skipped':
                color = Fore.BLUE
                status = "⏭️"
            else:
                color = Fore.RED
                status = "❌"
            
            self.stdout.write(f"{status} {color}{model_name}{Style.RESET_ALL}")
            
            for action in result.get('actions', []):
                self.stdout.write(f"   - {action}")
    
    def _display_orphaned_tables(self, orphaned_tables):
        """Display orphaned tables"""
        if not orphaned_tables:
            self.stdout.write(f"\n{Fore.GREEN}✅ No orphaned tables found!{Style.RESET_ALL}")
            return
        
        self.stdout.write(f"\n{Fore.YELLOW}⚠️  Orphaned Tables ({len(orphaned_tables)} found):{Style.RESET_ALL}")
        self.stdout.write("-" * 40)
        
        for table in orphaned_tables:
            self.stdout.write(f"🗃️  {table['name']} - {table['rows']} rows, {table['size_mb']} MB")
    
    def _handle_orphaned_tables(self, sync_engine, orphaned_tables, dry_run):
        """Handle dropping of orphaned tables with dependency awareness"""
        self.stdout.write(f"\n{Fore.YELLOW}Handling orphaned tables...{Style.RESET_ALL}")
        
        if dry_run:
            for table in orphaned_tables:
                table_name = table['name']
                self.stdout.write(f"[DRY RUN] Would drop table: {table_name}")
        else:
            try:
                # Use dependency-aware dropping to handle FK constraints properly
                result = sync_engine.drop_orphaned_tables_with_dependencies(orphaned_tables)
                
                # Report successful drops
                for table_name in result['dropped']:
                    self.stdout.write(f"{Fore.GREEN}✅ Dropped table: {table_name}{Style.RESET_ALL}")
                
                # Report failed drops
                for table_name in result['failed']:
                    self.stdout.write(f"{Fore.RED}❌ Failed to drop table: {table_name}{Style.RESET_ALL}")
                    
            except Exception as e:
                self.stdout.write(f"{Fore.RED}❌ Error dropping orphaned tables: {e}{Style.RESET_ALL}")
                # Fallback to individual dropping if dependency-aware method fails
                for table in orphaned_tables:
                    table_name = table['name']
                    try:
                        if sync_engine.drop_orphaned_table(table_name):
                            self.stdout.write(f"{Fore.GREEN}✅ Dropped table: {table_name}{Style.RESET_ALL}")
                        else:
                            self.stdout.write(f"{Fore.RED}❌ Failed to drop table: {table_name}{Style.RESET_ALL}")
                    except Exception as e:
                        self.stdout.write(f"{Fore.RED}❌ Error dropping {table_name}: {e}{Style.RESET_ALL}")
    
    def _generate_report(self, results, report_type):
        """Generate detailed report"""
        report_dir = get_setting('REPORT_OUTPUT_DIR', 'dbsync_reports/')
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if report_type in ['json', 'both']:
            json_file = os.path.join(report_dir, f'dbsync_report_{timestamp}.json')
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.stdout.write(f"{Fore.BLUE}JSON report: {json_file}{Style.RESET_ALL}")
        
        if report_type in ['html', 'both']:
            html_file = os.path.join(report_dir, f'dbsync_report_{timestamp}.html')
            self._generate_html_report(results, html_file, timestamp)
            self.stdout.write(f"{Fore.BLUE}HTML report: {html_file}{Style.RESET_ALL}")
    
    def _generate_html_report(self, results, html_file, timestamp):
        """Generate HTML report"""
        # Get version from settings
        version = get_setting('VERSION', '1.0.0')
        
        # Count results by status
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        warning_count = sum(1 for r in results.values() if r['status'] == 'warning')
        error_count = sum(1 for r in results.values() if r['status'] == 'error')
        skipped_count = sum(1 for r in results.values() if r['status'] == 'skipped')
        total_count = len(results)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django DB Sync Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }}
        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
        }}
        .success {{ background-color: #28a745; }}
        .warning {{ background-color: #ffc107; color: #212529; }}
        .error {{ background-color: #dc3545; }}
        .skipped {{ background-color: #007bff; }}
        .total {{ background-color: #6c757d; }}
        .results {{
            margin-top: 30px;
        }}
        .model-result {{
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }}
        .model-header {{
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }}
        .model-header.success {{ background-color: #d4edda; color: #155724; }}
        .model-header.warning {{ background-color: #fff3cd; color: #856404; }}
        .model-header.error {{ background-color: #f8d7da; color: #721c24; }}
        .model-header.skipped {{ background-color: #d1ecf1; color: #0c5460; }}
        .status-icon {{
            margin-right: 10px;
            font-size: 18px;
        }}
        .actions {{
            padding: 15px 20px;
            background-color: #f8f9fa;
        }}
        .action-item {{
            margin: 5px 0;
            padding: 5px 0;
            border-left: 3px solid #007bff;
            padding-left: 10px;
        }}
        .no-actions {{
            color: #6c757d;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Django Database Sync Report</h1>
            <div class="timestamp">Generated on {timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card success">
                <div style="font-size: 24px;">✅ {success_count}</div>
                <div>Successful</div>
            </div>
            <div class="summary-card warning">
                <div style="font-size: 24px;">⚠️ {warning_count}</div>
                <div>Warnings</div>
            </div>
            <div class="summary-card error">
                <div style="font-size: 24px;">❌ {error_count}</div>
                <div>Errors</div>
            </div>
            <div class="summary-card skipped">
                <div style="font-size: 24px;">⏭️ {skipped_count}</div>
                <div>Skipped</div>
            </div>
            <div class="summary-card total">
                <div style="font-size: 24px;">📊 {total_count}</div>
                <div>Total Models</div>
            </div>
        </div>
        
        <div class="results">
            <h2>📋 Detailed Results</h2>"""
        
        # Add each model result
        for model_name, result in results.items():
            status = result['status']
            actions = result.get('actions', [])
            warnings = result.get('warnings', [])
            errors = result.get('errors', [])
            
            # Status icon mapping
            status_icons = {
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'skipped': '⏭️'
            }
            
            icon = status_icons.get(status, '❓')
            
            html_content += f"""
            <div class="model-result">
                <div class="model-header {status}">
                    <span class="status-icon">{icon}</span>
                    <span>{model_name}</span>
                </div>
                <div class="actions">"""
            
            # Add actions, warnings, and errors
            all_items = []
            if actions:
                all_items.extend([(action, 'action') for action in actions])
            if warnings:
                all_items.extend([(warning, 'warning') for warning in warnings])
            if errors:
                all_items.extend([(error, 'error') for error in errors])
            
            if all_items:
                for item, item_type in all_items:
                    html_content += f'<div class="action-item">• {item}</div>'
            else:
                html_content += '<div class="no-actions">No actions required</div>'
            
            html_content += """
                </div>
            </div>"""
        
        # Close HTML
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generated by Django DB Sync v{version}</p>
            <p>Powerd By Lovedazzell</p>
            <p>Report created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
