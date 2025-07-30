import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class SubmitOrderCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'submit-order'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Submit order via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_id',
            required=True,
            help='File ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--model',
            required=True,
            help='Model name',
            type=str,
        )
        self._command_parser.add_argument(
            '--tags_ids',
            nargs='?',
            default=None,
            help='List of tags ids delimited by comma',
            type=str,
        )
        self._command_parser.add_argument(
            '--pdf_report_types',
            nargs='?',
            default=None,
            help='List of PDF report types',
            type=str,
        )
        self._command_parser.add_argument(
            '--pdf_metadata',
            nargs='?',
            default=None,
            help='PDF report metadata',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        tags_ids = None
        if args.tags_ids:
            tags_ids = [item.strip() for item in args.tags_ids.split(',')]
        pdf_report_types = None
        if args.pdf_report_types:
            pdf_report_types = [item.strip() for item in args.tags_ids.split(',')]
        pdf_metadata = None
        if args.pdf_metadata:
            pdf_metadata = json.loads(args.pdf_metadata)
        result = api_client.order_api.submit_order(
            file_id=args.file_id,
            model_name=args.model,
            tags_ids=tags_ids,
            pdf_report_types=pdf_report_types,
            pdf_metadata=pdf_metadata,
        )
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
