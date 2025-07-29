#!/usr/bin/env python3
#
# dotnetpe_payload.py
#
# Authors: jeFF0Falltrades, doomedraven
#
# Provides a wrapper class for accessing metadata from a DotNetPE object and
# performing data conversions
#
# MIT License
#
# Copyright (c) 2024 Jeff Archer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from dataclasses import dataclass
from hashlib import sha256
from logging import getLogger

from dnfile import dnPE
from yara import Rules

from ..config_parser_exception import ConfigParserException
from .data_utils import bytes_to_int
from .dotnet_constants import MDT_FIELD_DEF, MDT_METHOD_DEF, MDT_STRING

logger = getLogger(__name__)


# Helper class representing a single Method
@dataclass
class DotNetPEMethod:
    name: str
    offset: int
    rva: int
    size: int
    token: int


class DotNetPEPayload:
    def __init__(
        self, file_path: str, yara_rule: Rules = None, data: bytes = None
    ) -> None:
        self.file_path = file_path
        self.data = data
        if self.data is None:
            self.data = self._get_file_data()

        # Calculate SHA256
        sha256_obj = sha256()
        sha256_obj.update(self.data)
        self.sha256 = sha256_obj.hexdigest()

        self.dotnetpe: dnPE = None
        try:
            if self.data:
                self.dotnetpe = dnPE(data=self.data, clr_lazy_load=True)
            else:
                self.dotnetpe = dnPE(self.file_path, clr_lazy_load=True)
        except Exception:
            raise ConfigParserException("Failed to load project as dotnet executable")

        self.yara_match = ""
        if yara_rule is not None:
            self.yara_match = self._match_yara(yara_rule)

        # Pre-sort Method table for efficient lookups
        self._methods = self._generate_method_list()
        self._methods_by_offset = sorted(self._methods, key=lambda m: m.offset)
        self._methods_by_token = sorted(self._methods, key=lambda m: m.token)

    # Given a byte array's size and RVA, translates the RVA to the offset of
    # the byte array and returns the bytes of the array as a byte string
    def byte_array_from_size_and_rva(self, arr_size: int, arr_rva: int) -> bytes:
        arr_field_rva = self.fieldrva_from_rva(arr_rva)
        arr_offset = self.offset_from_rva(arr_field_rva)
        return self.data[arr_offset : arr_offset + arr_size]

    # Given an offset, and either a terminating offset or delimiter, extracts
    # the byte string
    def byte_string_from_offset(
        self, offset_start: int, offstart_end: int = -1, delimiter: bytes = b"\0"
    ) -> bytes:
        if offstart_end != -1:
            try:
                return self.data[offset_start:offstart_end]
            except Exception:
                raise ConfigParserException(
                    f"Could not extract string value from offset range [{hex(offset_start)}:{offstart_end}]"
                )
        try:
            return self.data[offset_start:].partition(delimiter)[0]
        except Exception:
            raise ConfigParserException(
                f"Could not extract string value from offset {hex(offset_start)} with delimiter {delimiter}"
            )

    # Given an RVA, derives the corresponding Field name
    def field_name_from_rva(self, rva: int) -> str:
        try:
            return self.dotnetpe.net.mdtables.Field.rows[
                (rva ^ MDT_FIELD_DEF) - 1
            ].Name.value
        except Exception:
            raise ConfigParserException(f"Could not find Field for RVA {rva}")

    # Given an RVA, derives the corresponding FieldRVA value
    def fieldrva_from_rva(self, rva: int) -> int:
        field_id = rva ^ MDT_FIELD_DEF
        for row in self.dotnetpe.net.mdtables.FieldRva:
            if row.struct.Field_Index == field_id:
                return row.struct.Rva
        raise ConfigParserException(f"Could not find FieldRVA for RVA {rva}")

    # Generates a list of DotNetPEMethod objects for efficient lookups of method
    # metadata in other operations
    def _generate_method_list(
        self,
    ) -> list[DotNetPEMethod]:
        method_objs = []

        for idx, method in enumerate(self.dotnetpe.net.mdtables.MethodDef.rows):
            method_offset = self.offset_from_rva(method.Rva)

            # Parse size from flags
            flags = self.data[method_offset]
            method_size = 0
            if flags & 3 == 2:  # Tiny format
                method_size = flags >> 2
            elif flags & 3 == 3:  # Fat format (add 12-byte header)
                method_size = 12 + bytes_to_int(
                    self.data[method_offset + 4 : method_offset + 8]
                )

            method_objs.append(
                DotNetPEMethod(
                    method.Name.value,
                    method_offset,
                    method.Rva,
                    method_size,
                    (MDT_METHOD_DEF ^ idx) + 1,
                )
            )
        return method_objs

    # Returns payload binary content
    def _get_file_data(self) -> bytes:
        logger.debug(f"Reading contents from: {self.file_path}")
        try:
            with open(self.file_path, "rb") as fp:
                data = fp.read()
        except Exception:
            raise ConfigParserException(f"Error reading from path: {self.file_path}")
        logger.debug(f"Successfully read {len(data)} bytes")
        return data

    # Tests a given YARA rule object against the file content,
    # returning the matching rule's name, or "No match"
    def _match_yara(self, rule: Rules) -> str:
        try:
            match = rule.match(data=self.data)
            return str(match[0]) if len(match) > 0 else "No match"
        except Exception as e:
            logger.exception(e)
            return f"Exception encountered: {e}"

    # Given a DotNetPEMethod, returns its body as raw bytes
    def method_body_from_method(self, method: DotNetPEMethod) -> bytes:
        return self.byte_string_from_offset(method.offset, method.offset + method.size)

    # Given a Method name, returns a list of DotNetPEMethods matching that name
    def methods_from_name(self, name: str) -> list[DotNetPEMethod]:
        return [method for method in self._methods if method.name == name]

    # Given the offset to an instruction, reverses the instruction to its
    # parent Method, optionally returning an adjacent Method using step to
    # signify the direction of adjacency, and using by_token to determine
    # whether to calculate adjacency by token or offset
    def method_from_instruction_offset(
        self, ins_offset: int, step: int = 0, by_token: bool = False
    ) -> DotNetPEMethod:
        for idx, method in enumerate(self._methods_by_offset):
            if method.offset <= ins_offset < method.offset + method.size:
                return (
                    self._methods_by_token[self._methods_by_token.index(method) + step]
                    if by_token
                    else self._methods_by_offset[idx + step]
                )
        raise ConfigParserException(
            f"Could not find method from instruction offset {hex(ins_offset)}"
        )

    # Given an RVA, returns a data/file offset
    def offset_from_rva(self, rva: int) -> int:
        return self.dotnetpe.get_offset_from_rva(rva)

    # Given an RVA, derives the corresponding User String
    def user_string_from_rva(self, rva: int) -> str:
        return self.dotnetpe.net.user_strings.get(rva ^ MDT_STRING).value

    def custom_attribute_from_type(self, typespacename: str, typename: str) -> dict:
        """
        Ex:
            typespacename: Server.Properties
            typenaem: Settings

        dnspy view
            // Server.Properties.Settings
            // Token: 0x17000077 RID: 119
            // (get) Token: 0x06000913 RID: 2323 RVA: 0x00009FED File Offset: 0x000081ED
            // (set) Token: 0x06000914 RID: 2324 RVA: 0x0000A004 File Offset: 0x00008204
            [DebuggerNonUserCode]
            [DefaultSettingValue("3128")]
            [UserScopedSetting]
            public decimal ReverseProxyPort

        returns: dict.
            Ex: {"ReverseProxyPort": "3128"}
        """
        config = {}
        try:
            for td in self.dotnetpe.net.mdtables.TypeDef.rows:
                if (
                    td.TypeNamespace.value != typespacename
                    and td.TypeName.value != typename
                ):
                    continue
                for pd_row_index, pd in enumerate(
                    self.dotnetpe.net.mdtables.Property.rows
                ):
                    if pd.Name.value.startswith(
                        "Boolean_",
                        "BorderStyle_",
                        "Color_",
                        "Byte",
                        "Int32_",
                        "SizeF_",
                        "String_",
                    ):
                        continue
                    for ca in self.dotnetpe.net.mdtables.CustomAttribute.rows:
                        if (
                            ca.Parent.row_index == pd_row_index + 1
                        ):  # CustomAttribute Parent index is 1-based
                            # Extract the value from the CustomAttribute blob
                            blob_data = ca.Value.value
                            if blob_data and blob_data != b"\x01\x00\x00\x00":
                                # Basic handling of the blob data. You might need to adjust this depending on the actual format.
                                # In many cases, the value is stored as a UTF-8 string after a preamble.
                                try:
                                    # Skip preamble bytes (usually 2 bytes). 3rd byte is size of data
                                    value_bytes = blob_data[3:]
                                    value = value_bytes.decode("utf-8").rstrip("\x00")
                                    config.setdefault(pd.Name.value, value)
                                except UnicodeDecodeError:
                                    logger.debug(
                                        "Warning: Could not decode blob data for %s",
                                        pd.Name.value,
                                    )
        except Exception as e:
            logger.debug("An error occurred in custom_attribute_from_type: %s", str(e))
        return config
