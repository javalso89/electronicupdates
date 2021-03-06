﻿' -----------------------------------------------------------------------
'  <copyright file="IMetadataApi.vb" company="Experian Data Quality">
'   Copyright (c) Experian. All rights reserved.
'  </copyright>
' -----------------------------------------------------------------------

''' <summary>
''' Defines the interface to the QAS Electronic Updates Metadata API.
''' </summary>
Public Interface IMetadataApi

    ''' <summary>
    ''' Returns the available updates packages.
    ''' </summary>
    ''' <returns>
    ''' The available updates packages.
    ''' </returns>
    Function GetAvailablePackages() As AvailablePackagesReply

    ''' <summary>
    ''' Gets the download <see cref="Uri"/> for the specified file.
    ''' </summary>
    ''' <param name="fileName">The name of the file to download.</param>
    ''' <param name="fileHash">The hash of the file to download.</param>
    ''' <param name="startAtByte">The byte to start downloading the file from.</param>
    ''' <param name="endAtByte">The byte to end downloading the file from.</param>
    ''' <returns>
    ''' The <see cref="Uri"/> to download the file specified by
    ''' <paramref name="fileName"/> and <paramref name="fileHash"/> from.
    ''' </returns>
    Function GetDownloadUri(ByVal fileName As String, ByVal fileHash As String, ByVal startAtByte As Long?, ByVal endAtByte As Long?) As Uri

    ''' <summary>
    ''' Gets or sets the password to use to authenticate with the service.
    ''' </summary>
    Property Password As String

    ''' <summary>
    ''' Gets or sets the user name to use to authenticate with the service.
    ''' </summary>
    Property UserName As String

End Interface