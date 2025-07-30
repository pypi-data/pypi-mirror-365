"""Output formatters for ScoutML CLI."""

import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, BarColumn, TextColumn
from rich.tree import Tree
from rich import box


def format_paper_table(
    papers: List[Dict[str, Any]],
    console: Console,
    show_scores: bool = False,
    show_benchmarks: bool = False
):
    """Format papers as a clean table followed by detailed cards."""
    # First, show a clean summary table
    table = Table(
        title="Search Results Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title_style="bold",
        caption=f"Showing {len(papers)} papers",
        caption_style="dim"
    )
    
    # Add columns
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="white", overflow="fold", max_width=60)
    table.add_column("Year", style="yellow", justify="center", width=6)
    table.add_column("Citations", style="green", justify="right", width=10)
    table.add_column("ArXiv", style="cyan", width=12)
    
    # Add summary rows
    for i, paper in enumerate(papers, 1):
        table.add_row(
            str(i),
            paper.get('title', paper.get('parsed_title', 'Unknown')),
            str(paper.get('year', 'N/A')),
            str(paper.get('citation_count', paper.get('citationcount', 0))),
            paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))
        )
    
    console.print(table)
    console.print("")  # Add spacing
    
    # Then show detailed information for each paper
    console.print("[bold]Detailed Results[/bold]")
    console.print("")
    
    for i, paper in enumerate(papers, 1):
        # Create a panel for each paper
        title = paper.get('title', paper.get('parsed_title', 'Unknown'))
        arxiv_id = paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))
        
        # Format authors - check multiple possible field names
        authors = paper.get('authors', paper.get('parsed_authors', paper.get('author_list', [])))
        
        # If still no authors, check if there's an author_names field
        if not authors and 'author_names' in paper:
            authors = paper.get('author_names', [])
        
        if isinstance(authors, list) and authors:
            # Clean author names (remove emails and affiliations if present)
            clean_authors = []
            for author in authors[:3]:
                # If author is a string, take only the name part (before email or newline)
                if isinstance(author, str):
                    name = author.split('@')[0].split('\n')[0].strip()
                    clean_authors.append(name)
                else:
                    clean_authors.append(str(author))
            author_str = ", ".join(clean_authors)
            if len(authors) > 3:
                author_str += f" et al. ({len(authors)} authors)"
        elif isinstance(authors, str) and authors:
            # Handle case where authors is a single string
            author_str = authors
        else:
            # Final fallback - check if there's any author-related field
            author_str = paper.get('author', paper.get('first_author', "Unknown"))
        
        # Build content sections
        content_parts = []
        
        # Basic info
        basic_info = f"[dim]Authors:[/dim] {author_str}\n"
        basic_info += f"[dim]Year:[/dim] {paper.get('year', 'N/A')} | "
        basic_info += f"[dim]Citations:[/dim] {paper.get('citation_count', 0)} | "
        basic_info += f"[dim]ArXiv:[/dim] {arxiv_id}"
        content_parts.append(basic_info)
        
        # Models
        models = paper.get('models_used', [])
        if models:
            content_parts.append(f"\n[bold]Models:[/bold] {', '.join(models)}")
        
        # Datasets
        datasets = paper.get('datasets', [])
        if datasets:
            content_parts.append(f"\n[bold]Datasets:[/bold] {', '.join(datasets)}")
        
        # Metrics
        metrics = paper.get('metrics', [])
        if metrics:
            content_parts.append(f"\n[bold]Metrics:[/bold] {', '.join(metrics)}")
        
        # Key Results - check multiple possible field names
        results = paper.get('results', paper.get('key_results', paper.get('main_results', [])))
        if results:
            results_text = "\n[bold]Key Results:[/bold]"
            for result in results:
                results_text += f"\n  • {result}"
            content_parts.append(results_text)
        
        # Create panel
        panel_content = "\n".join(content_parts)
        panel = Panel(
            panel_content,
            title=f"[bold]{i}. {title}[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(panel)
        
        if i < len(papers):
            console.print("")  # Add spacing between panels


def format_comparison_output(
    results: Dict[str, Any],
    console: Console,
    output_format: str = 'rich'
):
    """Format paper comparison results."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    papers = results['papers']
    comparison = results['comparison']
    matrix = results.get('comparison_matrix', {})
    
    if output_format == 'markdown':
        # Generate markdown
        md_content = f"# Paper Comparison\n\n"
        md_content += f"Comparing {len(papers)} papers:\n\n"
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', paper.get('parsed_title', 'Unknown Title'))
            year = paper.get('year', 'N/A')
            arxiv_id = paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))
            citations = paper.get('citation_count', paper.get('citationcount', 0))
            
            md_content += f"{i}. **{title}** ({year})\n"
            md_content += f"   - ArXiv: {arxiv_id}\n"
            md_content += f"   - Citations: {citations}\n\n"
        
        md_content += "## Analysis\n\n"
        md_content += comparison['comparison_text']
        
        console.print(Markdown(md_content))
        return
    
    # Rich output
    console.print(Panel.fit(
        f"[bold cyan]Comparing {len(papers)} Papers[/bold cyan]",
        border_style="cyan"
    ))
    
    # Show paper list
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', paper.get('parsed_title', 'Unknown Title'))
        year = paper.get('year', 'N/A')
        arxiv_id = paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))
        citations = paper.get('citation_count', paper.get('citationcount', 0))
        
        console.print(f"\n[bold]{i}.[/bold] {title} [dim]({year})[/dim]")
        console.print(f"   ArXiv: [cyan]{arxiv_id}[/cyan] | Citations: [green]{citations}[/green]")
    
    # Show comparison matrix if available
    if matrix:
        console.print("\n[bold]Comparison Matrix:[/bold]")
        
        # Methods comparison
        if 'methods' in matrix:
            console.print("\n[yellow]Methods:[/yellow]")
            for paper_id, methods in matrix['methods'].items():
                console.print(f"  {paper_id}: {', '.join(methods[:5])}")
        
        # Datasets comparison
        if 'datasets' in matrix:
            console.print("\n[yellow]Datasets:[/yellow]")
            for paper_id, datasets in matrix['datasets'].items():
                console.print(f"  {paper_id}: {', '.join(datasets[:5])}")
    
    # Show AI analysis
    console.print("\n[bold]AI Analysis:[/bold]")
    comparison_text = comparison.get('comparison_text', '')
    if comparison_text:
        # Don't truncate - show full comparison
        console.print(Panel(
            comparison_text,
            title="Detailed Comparison",
            border_style="green",
            expand=True
        ))


def format_review_output(
    results: Dict[str, Any],
    console: Console,
    output_format: str = 'rich'
):
    """Format literature review results."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    topic = results.get('topic', 'Unknown Topic')
    
    # Handle both old and new response formats
    if 'review' in results:
        # New format with nested review object
        review_data = results['review']
        synthesis = {
            'papers_analyzed': review_data.get('papers_analyzed', 0),
            'year_range': review_data.get('year_range', 'N/A'),
            'review_text': review_data.get('review_text', ''),
            'key_methods': review_data.get('key_methods', [])
        }
        key_papers = results.get('papers', [])
        timeline = {}
    else:
        # Old format
        synthesis = results.get('synthesis', {})
        key_papers = results.get('key_papers', [])
        timeline = results.get('timeline', {})
    
    if output_format == 'markdown':
        # Generate full markdown review
        md_content = f"# Literature Review: {topic}\n\n"
        md_content += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        md_content += f"**Papers analyzed:** {synthesis.get('papers_analyzed', 'N/A')}\n"
        
        # Handle year range
        if 'year_range' in synthesis:
            md_content += f"**Time span:** {synthesis['year_range']}\n\n"
        elif 'timeline' in synthesis and synthesis['timeline']:
            years = [item.get('year') for item in synthesis['timeline'] if 'year' in item]
            if years:
                md_content += f"**Time span:** {min(years)}-{max(years)}\n\n"
        
        md_content += synthesis.get('review_text', '')
        
        console.print(Markdown(md_content))
        return
    
    # Rich output
    console.print(Panel.fit(
        f"[bold cyan]Literature Review: {topic}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Stats
    console.print(f"\n[bold]Analysis Summary:[/bold]")
    console.print(f"• Papers analyzed: [green]{synthesis.get('papers_analyzed', 'N/A')}[/green]")
    
    # Year range - handle missing or different formats
    if 'year_range' in synthesis:
        console.print(f"• Year range: [yellow]{synthesis['year_range']}[/yellow]")
    elif 'timeline' in synthesis and synthesis['timeline']:
        # Extract year range from timeline
        years = [item.get('year') for item in synthesis['timeline'] if 'year' in item]
        if years:
            year_range = f"{min(years)}-{max(years)}"
            console.print(f"• Year range: [yellow]{year_range}[/yellow]")
    
    # Handle key methods properly
    key_methods = synthesis.get('key_methods', [])
    if isinstance(key_methods, list) and key_methods:
        methods_display = ', '.join(str(m) for m in key_methods[:5] if m)
    else:
        methods_display = 'N/A'
    console.print(f"• Key methods: {methods_display}")
    
    # Timeline
    if timeline:
        console.print("\n[bold]Research Timeline:[/bold]")
        tree = Tree("📅 Papers by Year")
        for year in sorted(timeline.keys(), reverse=True)[:5]:
            year_node = tree.add(f"[yellow]{year}[/yellow] ({timeline[year]['count']} papers)")
            for paper_title in timeline[year]['key_papers'][:2]:
                year_node.add(f"• {paper_title[:60]}...")
        console.print(tree)
    
    # Key papers
    if key_papers:
        console.print("\n[bold]Top 5 Key Papers:[/bold]")
        for i, paper in enumerate(key_papers[:5], 1):
            title = paper.get('title', paper.get('parsed_title', 'Unknown Title'))
            citations = paper.get('citation_count', paper.get('citationcount', 0))
            year = paper.get('year', 'N/A')
            
            console.print(f"\n[bold]{i}.[/bold] {title}")
            console.print(f"   [dim]Citations: {citations} | Year: {year}[/dim]")
            # Handle methods properly
            methods = paper.get('methods', [])
            if isinstance(methods, list) and methods:
                methods_str = ', '.join(str(m) for m in methods[:3] if m)
            else:
                methods_str = 'N/A'
            console.print(f"   [dim]Methods: {methods_str}[/dim]")
    
    # Review text
    console.print("\n[bold]Literature Review:[/bold]")
    review_text = synthesis.get('review_text', '')
    if review_text:
        display_text = review_text[:2000] + "..." if len(review_text) > 2000 else review_text
        console.print(Panel(
            display_text,
            title="Review Extract",
            border_style="green",
            padding=(1, 2)
        ))
    else:
        console.print("[dim]No review text available[/dim]")


def format_insights_output(
    results: Dict[str, Any],
    console: Console,
    insight_type: str,
    output_format: str = 'rich'
):
    """Format research insights output."""
    if output_format == 'json':
        console.print_json(json.dumps(results, indent=2))
        return
    
    if output_format == 'csv':
        # Extract relevant data for CSV based on insight type
        if insight_type == 'reproducibility':
            csv_content = export_to_csv(results.get('papers', []))
        elif insight_type == 'compute':
            # Convert trends to CSV
            trends = results.get('yearly_trends', [])
            csv_content = trends_to_csv(trends)
        else:  # funding
            sources = results.get('top_funding_sources', [])
            csv_content = funding_to_csv(sources)
        
        console.print(csv_content)
        return
    
    # Rich output based on insight type
    if insight_type == 'reproducibility':
        _format_reproducibility_insights(results, console)
    elif insight_type == 'compute':
        _format_compute_insights(results, console)
    else:  # funding
        _format_funding_insights(results, console)


def _format_reproducibility_insights(results: Dict[str, Any], console: Console):
    """Format reproducibility insights."""
    console.print(Panel.fit(
        "[bold cyan]Reproducibility Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Score distribution
    console.print("\n[bold]Score Distribution:[/bold]")
    dist = results.get('score_distribution', {})
    for score, count in dist.items():
        bar = "█" * int(count / max(dist.values()) * 30)
        console.print(f"  {score:>8}: {bar} {count}")
    
    # Top methods
    console.print("\n[bold]Most Reproducible Methods:[/bold]")
    for method in results.get('top_reproducible_methods', [])[:5]:
        console.print(f"  • {method['method']}: avg score {method['avg_score']:.2f} ({method['paper_count']} papers)")
    
    # Papers
    console.print(f"\n[bold]Top Reproducible Papers:[/bold] (Total: {results.get('total_count', 0)})")
    format_paper_table(results.get('papers', [])[:10], console)


def _format_compute_insights(results: Dict[str, Any], console: Console):
    """Format compute requirement insights."""
    console.print(Panel.fit(
        "[bold cyan]Compute Requirements Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Data quality note
    if results.get('data_quality_note'):
        console.print(f"\n[yellow]Note:[/yellow] {results['data_quality_note']}")
    
    # Overall stats
    if results.get('overall_gpu_stats'):
        stats = results['overall_gpu_stats']
        console.print("\n[bold]Overall GPU Statistics:[/bold]")
        console.print(f"  • Min GPUs: [green]{stats['min']}[/green]")
        console.print(f"  • Max GPUs: [red]{stats['max']}[/red]")
        console.print(f"  • Average: [yellow]{stats['avg']:.1f}[/yellow]")
        if 'median' in stats:
            console.print(f"  • Median: [blue]{stats['median']}[/blue]")
    
    # GPU types
    console.print("\n[bold]Popular GPU Types:[/bold]")
    for gpu_type, count in list(results.get('gpu_type_popularity', {}).items())[:5]:
        console.print(f"  • {gpu_type}: {count} papers")
    
    # Yearly trends
    if results.get('yearly_trends'):
        console.print("\n[bold]Recent Trends:[/bold]")
        for trend in results['yearly_trends'][-3:]:
            console.print(f"\n  [yellow]{trend['year']}:[/yellow]")
            console.print(f"    Papers: {trend['total_papers']} (with GPU info: {trend['papers_with_gpu_info']})")
            if trend.get('gpu_count_stats'):
                console.print(f"    Avg GPUs: {trend['gpu_count_stats']['avg']:.1f}")


def _format_funding_insights(results: Dict[str, Any], console: Console):
    """Format funding analysis insights."""
    console.print(Panel.fit(
        "[bold cyan]Funding Analysis[/bold cyan]",
        border_style="cyan"
    ))
    
    # Data quality note
    if results.get('data_quality_note'):
        console.print(f"\n[yellow]Note:[/yellow] {results['data_quality_note']}")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  • Total funded papers: {results.get('total_funded_papers', 0)}")
    console.print(f"  • Unique funding sources: {results.get('unique_funding_sources', 0)}")
    
    # Top sources
    console.print("\n[bold]Top Funding Sources by Impact:[/bold]")
    table = Table(box=box.SIMPLE)
    table.add_column("Source", style="cyan")
    table.add_column("Papers", justify="right")
    table.add_column("Avg Citations", justify="right")
    table.add_column("SOTA %", justify="right")
    
    for source in results.get('top_funding_sources', [])[:10]:
        table.add_row(
            source['source'][:40],
            str(source['paper_count']),
            f"{source['avg_citations']:.1f}",
            f"{source['sota_percentage']:.1f}%"
        )
    
    console.print(table)


# Export functions
def export_to_csv(papers: List[Dict[str, Any]]) -> str:
    """Export papers to CSV format with extended metadata."""
    output = io.StringIO()
    if not papers:
        return ""
    
    # Define fields to export - using actual field names from API
    fields = ['title', 'year', 'citation_count', 'arxiv_id', 'venue', 
              'authors', 'methods', 'models_used', 'datasets', 'metrics',
              'results', 'sota_status', 'domain', 'classification']
    
    # Create header with readable names
    headers = ['Title', 'Year', 'Citations', 'ArXiv ID', 'Venue',
               'Authors', 'Methods', 'Models', 'Datasets', 'Metrics',
               'Results', 'SOTA', 'Domain', 'Classification']
    
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    # Write custom header
    output.write(','.join(headers) + '\n')
    
    for paper in papers:
        # Convert lists to strings
        row = {}
        for field in fields:
            value = paper.get(field, '')
            if isinstance(value, list):
                # Join list items with semicolon
                row[field] = '; '.join(str(item) for item in value)
            elif isinstance(value, bool):
                row[field] = 'Yes' if value else 'No'
            else:
                row[field] = str(value) if value else ''
        
        writer.writerow(row)
    
    return output.getvalue()


def export_to_json(data: Any, filepath: str):
    """Export data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_markdown(papers: List[Dict[str, Any]]) -> str:
    """Export papers to markdown format with extended metadata."""
    md = "# Search Results\n\n"
    
    for i, paper in enumerate(papers, 1):
        md += f"## {i}. {paper.get('title', paper.get('parsed_title', 'Unknown'))}\n\n"
        md += f"- **Year**: {paper.get('year', 'N/A')}\n"
        md += f"- **Citations**: {paper.get('citation_count', paper.get('citationcount', 0))}\n"
        md += f"- **ArXiv**: {paper.get('arxiv_id', paper.get('ArXiv', 'N/A'))}\n"
        md += f"- **Venue**: {paper.get('venue', 'N/A')}\n"
        md += f"- **Domain**: {paper.get('domain', 'N/A')}\n"
        md += f"- **Classification**: {paper.get('classification', 'N/A')}\n"
        md += f"- **SOTA**: {'Yes' if paper.get('sota_status', False) else 'No'}\n"
        
        authors = paper.get('authors', paper.get('parsed_authors', []))
        if authors:
            md += f"- **Authors**: {', '.join(authors[:5])}"
            if len(authors) > 5:
                md += " et al."
            md += "\n"
        
        # Technical details
        md += "\n### Technical Details\n\n"
        
        methods = paper.get('methods', [])
        if methods:
            md += f"- **Methods**: {', '.join(methods)}\n"
        
        models = paper.get('models_used', [])
        if models:
            md += f"- **Models**: {', '.join(models)}\n"
        
        datasets = paper.get('datasets', [])
        if datasets:
            md += f"- **Datasets**: {', '.join(datasets)}\n"
        
        metrics = paper.get('metrics', [])
        if metrics:
            md += f"- **Metrics**: {', '.join(metrics)}\n"
        
        # Results
        results = paper.get('results', [])
        if results:
            md += "\n### Key Results\n\n"
            for result in results:
                md += f"- {result}\n"
        
        if paper.get('abstract'):
            md += f"\n### Abstract\n\n{paper['abstract'][:500]}...\n"
        
        md += "\n---\n\n"
    
    return md


def trends_to_csv(trends: List[Dict[str, Any]]) -> str:
    """Convert trend data to CSV."""
    output = io.StringIO()
    if not trends:
        return ""
    
    writer = csv.writer(output)
    writer.writerow(['Year', 'Total Papers', 'Papers with GPU Info', 'Avg GPUs', 'Top GPU Type'])
    
    for trend in trends:
        gpu_stats = trend.get('gpu_count_stats', {})
        top_gpu = list(trend.get('top_gpu_types', {}).keys())[0] if trend.get('top_gpu_types') else 'N/A'
        
        writer.writerow([
            trend['year'],
            trend['total_papers'],
            trend['papers_with_gpu_info'],
            f"{gpu_stats.get('avg', 0):.1f}" if gpu_stats else 'N/A',
            top_gpu
        ])
    
    return output.getvalue()


def funding_to_csv(sources: List[Dict[str, Any]]) -> str:
    """Convert funding data to CSV."""
    output = io.StringIO()
    if not sources:
        return ""
    
    writer = csv.DictWriter(output, fieldnames=['source', 'paper_count', 'avg_citations', 'sota_percentage'])
    writer.writeheader()
    writer.writerows(sources)
    
    return output.getvalue()


def format_implementation_guide(guide: Dict[str, Any], console: Console):
    """Format implementation guide output."""
    console.print(f"\n[bold cyan]Implementation Guide for:[/bold cyan] {guide['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {guide['paper_info']['arxiv_id']}[/dim]")
    console.print(f"[dim]Complexity: {guide['paper_info']['complexity'].upper()}[/dim]\n")
    
    # Prerequisites
    console.print("[bold]Prerequisites:[/bold]")
    for prereq in guide['prerequisites']:
        console.print(f"\n  [cyan]{prereq['category']}:[/cyan]")
        for item in prereq['items']:
            console.print(f"    • {item}")
    
    # Implementation roadmap
    console.print("\n[bold]Implementation Roadmap:[/bold]")
    for phase in guide.get('implementation_roadmap', {}).get('phases', []):
        # Handle different duration formats
        duration = phase.get('duration', f"{phase.get('duration_days', 'Unknown')} days")
        console.print(f"\n  [bold cyan]Phase {phase.get('phase', '?')}: {phase.get('name', 'Unknown')}[/bold cyan] ({duration})")
        # Handle tasks - could be strings or dicts
        tasks = phase.get('tasks', [])
        for task in tasks:
            if isinstance(task, str):
                console.print(f"    ✓ {task}")
            elif isinstance(task, dict):
                task_desc = task.get('task', task.get('description', str(task)))
                console.print(f"    ✓ {task_desc}")
    
    # Key components - handle both old and new formats
    if 'key_components' in guide:
        console.print("\n[bold]Key Components:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Type")
        table.add_column("Critical", style="red")
        table.add_column("Notes")
        
        for comp in guide['key_components']:
            table.add_row(
                comp.get('name', 'Unknown'),
                comp.get('type', 'N/A'),
                "Yes" if comp.get('critical', False) else "No",
                comp.get('implementation_notes', comp.get('notes', ''))
            )
        console.print(table)
    elif 'architecture' in guide and 'key_components' in guide['architecture']:
        # Handle new AI response format
        console.print("\n[bold]Key Components:[/bold]")
        for comp in guide['architecture']['key_components']:
            console.print(f"\n  [cyan]{comp.get('name', 'Unknown')}[/cyan]")
            console.print(f"    Purpose: {comp.get('purpose', 'N/A')}")
            if 'interfaces' in comp:
                console.print(f"    Interfaces: {', '.join(comp['interfaces'])}")
    
    # Time estimate - handle both formats
    if 'estimated_time' in guide:
        time_est = guide['estimated_time']
        console.print(f"\n[bold]Estimated Time:[/bold]")
        console.print(f"  Minimum: {time_est.get('minimum_days', 'N/A')} days")
        console.print(f"  Expected: {time_est.get('expected_days', 'N/A')} days")
        console.print(f"  Maximum: {time_est.get('maximum_days', 'N/A')} days")
    elif 'overview' in guide and 'estimated_time_days' in guide['overview']:
        console.print(f"\n[bold]Estimated Time:[/bold] {guide['overview']['estimated_time_days']} days")
    elif 'implementation_guide' in guide and 'overview' in guide['implementation_guide']:
        overview = guide['implementation_guide']['overview']
        if 'estimated_time_days' in overview:
            console.print(f"\n[bold]Estimated Time:[/bold] {overview['estimated_time_days']} days")
    
    # Resources - handle multiple formats
    if guide.get('reference_implementations'):
        console.print("\n[bold]Reference Implementations:[/bold]")
        for ref in guide['reference_implementations'][:3]:
            console.print(f"  • {ref.get('title', ref.get('name', 'Unknown'))}")
            console.print(f"    [dim]{ref.get('code_url', ref.get('url', 'N/A'))}[/dim]")
    elif guide.get('resources') and guide['resources'].get('similar_implementations'):
        console.print("\n[bold]Reference Implementations:[/bold]")
        for ref in guide['resources']['similar_implementations'][:3]:
            console.print(f"  • {ref.get('name', 'Unknown')}")
            console.print(f"    [dim]{ref.get('url', 'N/A')}[/dim]")


def format_research_critique(critique: Dict[str, Any], console: Console):
    """Format research critique output."""
    console.print(f"\n[bold cyan]Research Critique:[/bold cyan] {critique['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {critique['paper_info']['arxiv_id']} | Year: {critique['paper_info']['year']} | Citations: {critique['paper_info']['citations']}[/dim]\n")
    
    # Overall assessment
    assessment = critique['overall_assessment']
    scores = assessment['scores']
    
    console.print("[bold]Overall Assessment:[/bold]")
    console.print(f"  Recommendation: [bold]{assessment['recommendation']}[/bold]")
    console.print(f"  Scores: Novelty={scores['novelty']}/10 | Impact={scores['impact']}/10 | Technical={scores['technical_quality']}/10 | Overall={scores['overall']}/10")
    
    # Strengths and weaknesses
    console.print("\n[bold green]Strengths:[/bold green]")
    for strength in assessment['strengths']:
        console.print(f"  ✓ {strength}")
    
    console.print("\n[bold red]Weaknesses:[/bold red]")
    for weakness in assessment['weaknesses']:
        console.print(f"  ✗ {weakness}")
    
    # Detailed critique
    for aspect, details in critique['detailed_critique'].items():
        console.print(f"\n[bold]{aspect.title()} Analysis:[/bold]")
        
        if details.get('strengths'):
            console.print("  [green]Strengths:[/green]")
            for s in details['strengths']:
                console.print(f"    • {s}")
        
        if details.get('weaknesses'):
            console.print("  [red]Weaknesses:[/red]")
            for w in details['weaknesses']:
                console.print(f"    • {w}")
        
        if details.get('suggestions'):
            console.print("  [yellow]Suggestions:[/yellow]")
            for s in details['suggestions']:
                console.print(f"    → {s}")
    
    # Improvement suggestions
    if critique.get('improvement_suggestions'):
        console.print("\n[bold]Top Improvement Suggestions:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Category")
        table.add_column("Suggestion")
        table.add_column("Priority")
        table.add_column("Effort")
        
        for sugg in critique['improvement_suggestions'][:5]:
            table.add_row(
                str(sugg['id']),
                sugg['category'],
                sugg['suggestion'],
                sugg['priority'].upper(),
                sugg['effort'].title()
            )
        console.print(table)


def format_limitation_solutions(solutions: Dict[str, Any], console: Console):
    """Format limitation solutions output."""
    console.print(f"\n[bold cyan]Limitation Solutions for:[/bold cyan] {solutions['paper_info']['title']}")
    console.print(f"[dim]ArXiv ID: {solutions['paper_info']['arxiv_id']}[/dim]\n")
    
    # Identified limitations
    console.print("[bold]Identified Limitations:[/bold]")
    for lim in solutions['identified_limitations']:
        severity_color = {"high": "red", "medium": "yellow", "low": "green"}[lim['severity']]
        console.print(f"\n  [{severity_color}]{lim['severity'].upper()}[/{severity_color}] - {lim['category'].title()}")
        console.print(f"  {lim['description']}")
    
    # Solutions for each limitation
    console.print("\n[bold]Proposed Solutions:[/bold]")
    for sol_set in solutions['solutions']:
        lim = sol_set['limitation']
        console.print(f"\n[bold cyan]For: {lim['description']}[/bold cyan]")
        
        for i, solution in enumerate(sol_set['proposed_solutions'], 1):
            console.print(f"\n  {i}. [bold]{solution['approach']}[/bold]")
            console.print(f"     {solution['description']}")
            console.print(f"     [dim]Tradeoff: {solution['tradeoff']}[/dim]")
            console.print(f"     [dim]Complexity: {solution['implementation_complexity']} | Expected: {solution['expected_improvement']}[/dim]")
            
            if solution.get('techniques'):
                console.print("     Techniques:")
                for tech in solution['techniques']:
                    console.print(f"       • {tech}")
    
    # Cross-paper solutions
    if solutions.get('cross_paper_solutions'):
        console.print("\n[bold]Cross-Paper Solutions:[/bold]")
        for cross_sol in solutions['cross_paper_solutions']:
            console.print(f"\n  {cross_sol['solution']}")
            console.print("  Related papers:")
            for paper in cross_sol['papers'][:3]:
                console.print(f"    • {paper['title']} ({paper['arxiv_id']})")


def format_experiment_design(design: Dict[str, Any], console: Console):
    """Format experiment design output."""
    console.print(f"\n[bold cyan]Experiment Design[/bold cyan]")
    console.print(f"[bold]Paper:[/bold] {design['paper_info']['title']}")
    console.print(f"[bold]Hypothesis:[/bold] {design['hypothesis']}\n")
    
    # Experiment plan
    plan = design['experiment_plan']
    console.print(f"[bold]Experiment Type:[/bold] {plan['experiment_type'].replace('_', ' ').title()}")
    
    console.print("\n[bold]Execution Plan:[/bold]")
    for phase in plan['phases']:
        console.print(f"\n  [bold cyan]Phase {phase['phase']}: {phase['name']}[/bold cyan] ({phase['duration']})")
        for task in phase['tasks']:
            console.print(f"    • {task}")
    
    # Baselines
    console.print("\n[bold]Baselines:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Baseline", style="cyan")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Description")
    
    for baseline in design['baselines']:
        table.add_row(
            baseline['name'],
            baseline['type'],
            baseline['implementation_status'],
            baseline['description'][:50] + "..." if len(baseline['description']) > 50 else baseline['description']
        )
    console.print(table)
    
    # Evaluation protocol
    protocol = design['evaluation_protocol']
    console.print("\n[bold]Evaluation Protocol:[/bold]")
    console.print(f"  Primary metrics: {', '.join(protocol['primary_metrics'])}")
    console.print(f"  Secondary metrics: {', '.join(protocol['secondary_metrics'])}")
    console.print(f"  Datasets: {', '.join(protocol['datasets'])}")
    
    # Expected outcomes
    outcomes = design['expected_outcomes']
    console.print("\n[bold]Expected Outcomes:[/bold]")
    console.print("  Success criteria:")
    for criterion in outcomes['success_criteria']:
        console.print(f"    ✓ {criterion}")
    
    # Risk analysis
    risks = design['risk_analysis']
    risk_color = {"high": "red", "medium": "yellow", "low": "green"}[risks['overall_risk_level']]
    console.print(f"\n[bold]Risk Analysis:[/bold] [{risk_color}]{risks['overall_risk_level'].upper()} RISK[/{risk_color}]")
    
    all_risks = risks['technical_risks'] + risks['resource_risks'] + risks['timeline_risks']
    if all_risks:
        for risk in all_risks[:3]:  # Show top 3 risks
            impact_color = {"high": "red", "medium": "yellow", "low": "green"}[risk['impact']]
            console.print(f"  • {risk['risk']} ([{impact_color}]{risk['impact']}[/{impact_color}])")
            console.print(f"    Mitigation: {risk['mitigation']}")
    
    # Timeline
    timeline = design['timeline']
    console.print(f"\n[bold]Timeline:[/bold] {timeline['total_duration']}")
    console.print("  Key milestones:")
    for milestone in timeline['milestones'][:4]:
        console.print(f"    Week {milestone['week']}: {milestone['milestone']}")