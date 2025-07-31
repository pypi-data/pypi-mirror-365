import asyncio
import logging
import os
import sys
import click
from dotenv import load_dotenv


def setup_logger(level: int) -> logging.Logger:
    """Configure and return a logger with the specified level."""
    logger = logging.getLogger(__name__)
    
    # Éviter la duplication si déjà configuré
    if logger.handlers:
        logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.option(
    "--env-file", 
    type=click.Path(exists=True, dir_okay=False), 
    help="Path to .env file"
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type (stdio, sse, or streamable-http)",
)
def main(verbose: int, env_file: str | None, transport: str):
    """Main entry point for the axians-mcp server."""
    
    # Configuration du logging
    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logger = setup_logger(log_level)
    
    logger.debug(f"Logging level set to: {logging.getLevelName(log_level)}")

    # Chargement des variables d'environnement
    if env_file:
        logger.debug(f"Loading environment from file: {env_file}")
        load_dotenv(env_file, override=True)
    else:
        logger.debug("Loading environment from default .env file if it exists")
        load_dotenv(override=True)

    # Détermination du transport final
    final_transport = _determine_transport(transport, logger)
    logger.debug(f"Final transport: {final_transport}")

    # Démarrage du serveur
    try:
        logger.debug("Starting server...")
        from .servers import main_mcp
        
        asyncio.run(main_mcp.run_async(transport=final_transport))
        
    except ImportError as e:
        logger.error(f"Failed to import server module: {e}")
        sys.exit(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Server shutdown initiated")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


def _determine_transport(cli_transport: str, logger: logging.Logger) -> str:
    """Determine the final transport to use based on CLI and environment."""
    
    def was_option_provided(ctx: click.Context, param_name: str) -> bool:
        source = ctx.get_parameter_source(param_name)
        return source not in (
            click.core.ParameterSource.DEFAULT_MAP,
            click.core.ParameterSource.DEFAULT
        )
    
    # Priorité : CLI > ENV > default
    env_transport = os.getenv("TRANSPORT", "stdio").lower()
    
    click_ctx = click.get_current_context(silent=True)
    if click_ctx and was_option_provided(click_ctx, "transport"):
        final_transport = cli_transport
    else:
        final_transport = env_transport
    
    # Validation
    valid_transports = ["stdio", "sse", "streamable-http"]
    if final_transport not in valid_transports:
        logger.warning(
            f"Invalid transport '{final_transport}', using 'stdio'"
        )
        final_transport = "stdio"
    
    return final_transport


if __name__ == "__main__":
    main()