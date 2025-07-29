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


''' Family of exceptions for package internals. '''


import contextlib as _contextlib
import logging as _logging

import exceptiongroup as _exceptiongroup

from . import imports as __


class Omniexception(
    __.immut.Object, BaseException,
    instances_mutables = ( '__cause__', ), # for PyPy
    instances_visibles = (
        '__cause__', '__context__', __.immut.is_public_identifier ),
):
    ''' Base for all exceptions raised internally. '''


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised internally. '''


class AddressLocateFailure( Omnierror, LookupError ):
    ''' Failure to locate address. '''

    def __init__(
        self, subject: str, address: __.cabc.Sequence[ str ], part: str
    ):
        super( ).__init__(
            f"Could not locate part '{part}' of address '{address}' "
            f"in {subject}." )


class AsyncAssertionFailure( Omnierror, AssertionError, TypeError ):
    ''' Assertion of awaitability of entity failed. '''

    def __init__( self, entity: __.typx.Any ):
        super( ).__init__( f"Entity must be awaitable: {entity!r}" )


class EntryAssertionFailure( Omnierror, AssertionError, KeyError ):
    ''' Assertion of entry in dictionary failed. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__( f"Could not find entry '{name}' in {subject}." )


class OperationInvalidity( Omnierror, RuntimeError ):
    ''' Invalid operation. '''

    def __init__( self, subject: str, name: str ):
        super( ).__init__(
            f"Could not perform operation '{name}' on {subject}." )


@_contextlib.contextmanager
def report_exceptions(
    scribe: _logging.Logger,
    message: str,
    eclass: type[ BaseException ] = SystemExit,
    eposargs: __.cabc.Sequence[ __.typx.Any ] = ( 1, ),
) -> __.cabc.Generator[ None, None, None ]:
    ''' Intercepts and reports exceptions.

        By default, raises ``SystemExit( 1 )``.
    '''
    level = scribe.getEffectiveLevel( )
    try: yield
    except _exceptiongroup.ExceptionGroup as excg: # pyright: ignore
        scribe.error( message )
        for exc in excg.exceptions: # pyright: ignore
            if level <= _logging.DEBUG: # noqa: SIM108
                nomargs = dict( exc_info = exc ) # pyright: ignore
            else: nomargs = { }
            scribe.error(
                f"\tCause: {exc}", **nomargs ) # pyright: ignore
        if eclass: raise eclass( *eposargs ) from None
    except Exception as exc:
        if level <= _logging.DEBUG: scribe.exception( f"{message}" )
        else: scribe.error( f"{message} Cause: {exc}" )
        if eclass: raise eclass( *eposargs ) from None
