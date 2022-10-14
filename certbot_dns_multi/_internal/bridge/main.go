package main

// #include <stdlib.h>
// #include <Python.h>
// int PyArg_ParseTuple_U(PyObject*, PyObject**);
import "C"

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"unsafe"

	"github.com/go-acme/lego/v4/challenge"
	"github.com/go-acme/lego/v4/providers/dns"
)

var (
	selectedProvider challenge.Provider
)

type configure struct {
	Provider    string            `json:"provider"`
	Credentials map[string]string `json:"credentials"`
}

type perform struct {
	Domain           string `json:"domain"`
	Token            string `json:"token"`
	KeyAuthorization string `json:"key_authorization"`
}

type cleanup perform

type response struct {
	Success bool   `json:"success"`
	Error   string `json:"error,omitempty"`
}

//export lego_bridge_cmd
func lego_bridge_cmd(self *C.PyObject, args *C.PyObject) *C.PyObject {
	var obj *C.PyObject
	if C.PyArg_ParseTuple_U(args, &obj) == 0 {
		return nil
	}
	bytes := C.PyUnicode_AsUTF8String(obj)
	defer C.Py_DecRef(bytes)
	cstr := C.PyBytes_AsString(bytes)
	str := C.GoString(cstr)

	action, err := next(str)
	if err != nil {
		return makeError(fmt.Errorf("parsing error: %w", err))
	}
	switch action := action.(type) {
	case *configure:
		for key, value := range action.Credentials {
			os.Setenv(key, value)
		}
		provider, err := dns.NewDNSChallengeProviderByName(action.Provider)
		if err != nil {
			return makeError(err)
		}
		selectedProvider = provider
		return makeSuccess()
	case *perform:
		if selectedProvider == nil {
			return makeError(errors.New("no provider selected, configure first"))
		}

		if err := selectedProvider.Present(
			action.Domain, action.Token, action.KeyAuthorization); err != nil {
			return makeError(err)
		}
		return makeSuccess()
	case *cleanup:
		if selectedProvider == nil {
			return makeError(errors.New("no provider selected, configure first"))
		}
		if err := selectedProvider.CleanUp(
			action.Domain, action.Token, action.KeyAuthorization); err != nil {
			return makeError(err)
		}
		return makeSuccess()
	default:
		return makeError(errors.New("unknown command"))
	}
}

func next(inputStr string) (any, error) {
	var v struct {
		Action string `json:"action"`
	}

	input := []byte(inputStr)
	if err := json.Unmarshal(input, &v); err != nil {
		return nil, fmt.Errorf("failed to parse json: %w", err)
	}
	um := func(dest any) any {
		if err := json.Unmarshal(input, dest); err != nil {
			return nil
		}
		return dest
	}
	switch v.Action {
	case "configure":
		return um(&configure{}), nil
	case "perform":
		return um(&perform{}), nil
	case "cleanup":
		return um(&cleanup{}), nil
	default:
		return nil, fmt.Errorf("unknown action '%s'", v.Action)
	}
}

func makeSuccess() *C.PyObject {
	return makeResponse(response{Success: true})
}

func makeError(err error) *C.PyObject {
	return makeResponse(response{
		Success: false,
		Error:   err.Error(),
	})
}

func makeResponse(r response) *C.PyObject {
	buf, _ := json.Marshal(r)
	cStr := C.CString(string(buf))
	pyStr := C.PyUnicode_FromString(cStr)
	C.free(unsafe.Pointer(cStr))
	return pyStr
}

func main() {
	panic("This is not a command-line program.")
}
