# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Support for edits on nested dictionaries. '''
# TODO: Independent package.
# TODO: Copying edits, not just in-place edits.


from . import imports as __
from . import nomina as _nomina
from . import exceptions as _exceptions


class Edit(
    __.immut.DataclassProtocol, __.typx.Protocol,
    decorators = ( __.typx.runtime_checkable, ),
):
    ''' Base representation of an edit to configuration. '''

    address: __.cabc.Sequence[ str ]

    @__.abc.abstractmethod
    def __call__( self, configuration: _nomina.NominativeDictionary ) -> None:
        ''' Performs edit. '''
        raise NotImplementedError

    def dereference(
        self, configuration: _nomina.NominativeDictionary
    ) -> __.typx.Any:
        ''' Dereferences value at address in configuration. '''
        configuration_ = configuration
        for part in self.address:
            if part not in configuration_:
                raise (
                    _exceptions.AddressLocateFailure( # noqa: TRY003
                        'configuration dictionary', self.address, part ) )
            configuration_ = configuration_[ part ]
        return configuration_

    def inject(
        self, configuration: _nomina.NominativeDictionary, value: __.typx.Any
    ) -> None:
        ''' Injects value at address in configuration. '''
        configuration_ = configuration
        for part in self.address[ : -1 ]:
            if part not in configuration_: configuration_[ part ] = { }
            configuration_ = configuration_[ part ]
        configuration_[ self.address[ -1 ] ] = value


class ElementsEntryEdit( Edit ):
    ''' Applies entry edit to every matching dictionary in array. '''

    editee: tuple[ str, __.typx.Any ]
    identifier: __.typx.Optional[ tuple[ str, __.typx.Any ] ] = None

    def __call__( self, configuration: _nomina.NominativeDictionary ) -> None:
        array = self.dereference( configuration )
        if self.identifier:
            iname, ivalue = self.identifier
        else: iname, ivalue = None, None
        ename, evalue = self.editee
        for element in array:
            if iname:
                if iname not in element:
                    raise _exceptions.EntryAssertionFailure( # noqa: TRY003
                        'configuration array element', iname )
                if ivalue != element[ iname ]: continue
            element[ ename ] = evalue


class SimpleEdit( Edit ):
    ''' Applies edit to single entity. '''

    value: __.typx.Any

    def __call__( self, configuration: _nomina.NominativeDictionary ) -> None:
        self.inject( configuration, self.value )


Edits: __.typx.TypeAlias = __.cabc.Iterable[ Edit ]
